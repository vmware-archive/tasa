# -*- coding: utf-8 -*-
#Django specific imports
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from webserver.settings import MEDIA_ROOT
from pkg_resources import resource_string
#Python std lib imports
import psycopg2
import os, time, json
from operator import itemgetter
#Webserver related imports
from webserver.common.dbconnector import DBConnect
from webserver.GPSentiDemo.sentiment_sql_templates import *

SEARCH_TERM = 'sr_trm'
SENTI_HTML_FORM = resource_string('webserver.common.resources.html','sentiment_input_page.html').encode('utf-8')

conn = DBConnect()
	
@csrf_exempt
def senti_home(request):
    '''Handles request that comes from a webpage (where a form is displayed for the user to enter the opinion string'''
    return HttpResponse(SENTI_HTML_FORM)

@csrf_exempt
def multi_series_sentiment_plot(request):
    ''' Return a multi-series sentiment plot '''
    search_term = request.REQUEST[SEARCH_TERM]
    sql = getMultiSeriesSentimentSQl(search_term)
    executionStatus, rows = conn.fetchRows(sql)  
    dt_count_lst = [(r.get('posted_date'),r.get('positive_count'), r.get('negative_count'), r.get('neutral_count')) for r in rows]
    dt_count_lst = sorted(dt_count_lst,key=itemgetter(0),reverse=False)
    dt_count_dict = {'multi_series':[{'posted_date':str(elem[0]),'positive_count':elem[1], 'negative_count':elem[2], 'neutral_count':elem[3]} for elem in dt_count_lst]}    
    print 'dt_count_lst:\n','\n'.join(['\t'.join([str(elem[0]),str(elem[1]), str(elem[2]), str(elem[3])]) for elem in dt_count_lst])

    return HttpResponse(json.dumps(dt_count_dict),content_type='application/json')    

@csrf_exempt
def dayhour_hmap(request):
    '''
        Return a Day-Hour heatmap of tweets for the search term
    '''
    search_term = request.REQUEST[SEARCH_TERM]
    sql = getDayHourHeatMapSQL(search_term)
    executionStatus, rows = conn.fetchRows(sql)  
    hmap_lst = [{'day':r.get('day_of_week'),'hour':r.get('hour_of_day'),'num_tweets':r.get('num_tweets'), 'msi':r.get('mean_sentiment_index')} for r in rows]
    response_dict = {'hmap':hmap_lst}

    return HttpResponse(json.dumps(response_dict),content_type='application/json')

@csrf_exempt
def generate_adjectives_cloud(request):
    '''
       Return a dict of adjectives and their frequencies associated with the search term.
    '''
    search_term = request.REQUEST[SEARCH_TERM]
    sql = getAdjectivesCloud(search_term)
    executionStatus, rows = conn.fetchRows(sql)  
    adjective_dict = [{'word':r.get('token'),'normalized_frequency':r.get('normalized_frequency')} for r in rows]

    response_dict = {'adjective_cloud':adjective_dict}
    return HttpResponse(json.dumps(response_dict),content_type='application/json')
	
@csrf_exempt
def topic_cloud_home(request):
    '''Handles request that comes from a webpage (where a form is displayed for the user to enter the opinion string'''
    payload = resource_string('webserver.common.resources.html','sample_topiccloud_payload.txt').encode('utf-8')
    html_page = resource_string('webserver.common.resources.html','generate_topic_cloud.html').encode('utf-8')
    return HttpResponse(html_page.replace('##SAMPLE_TOPICCLOUD_PLACEHOLDER##',payload))

@csrf_exempt
def generate_topic_cloud_from_form(request):
    '''
       This is a stand-alone topic cloud generator from data pasted on a form
       The form input should be of the form [topic_number; word; frequency]
    '''    
    input = request.POST['payload']
    triplets_arr = [item.split(';') for item in filter(lambda x: x!='', input.split('\n'))]
    #print 'triplets_arr :',triplets_arr
    #Ignore header
    triplets_arr = triplets_arr[1:]

    topic_words_dict = {}
    for triplet in triplets_arr:
        if(len(triplet)!=3):
            continue
        topic = triplet[0].strip()
        word = triplet[1].strip()
        freq = float(triplet[2].strip())
        if(topic_words_dict.has_key(topic)):
             topic_words_dict[topic].append({'word':word, 'normalized_frequency':freq})
        else:
             topic_words_dict[topic] = [{'word':word, 'normalized_frequency':freq}]

    #Normalize the frequency by max value of frequency in each topic
    for topic in topic_words_dict.keys():
        max_freq = max([item['normalized_frequency'] for item in topic_words_dict[topic]])
        for item in topic_words_dict[topic]:
            item['normalized_frequency'] /= max_freq

    #Create topic_cloud_dict
    topic_cloud_dict = {}
    for topic in topic_words_dict.keys():
        topic_div_id = 'topic_cloud_{0}'.format(topic)
        topic_cloud_dict[topic]= {'id':topic_div_id,'word_freq_list':topic_words_dict[topic]}        


    #Return an HTML table and a dict from which a word cloud will be generated.
    header_bgcolor="#2E8B57"
    cell_bgcolor='white'
    TABLE = '<table style="border:1; border-collapse:collapse;padding:3px" width="800">{0}</table>'
    TR = '<tr>{0}</tr>'
    TD = '<td style="border:1px solid black;" bgcolor={bgcolor}><h3 align="center">{content}</h3></td>'
    TD_WITH_ID = '<td id="{id}" style="border:1px solid black;" bgcolor={bgcolor}><h3 align="center">{content}</h3></td>'
    TH = '<td style="border:1px solid black;" bgcolor={bgcolor}><h2 align="center">{content}</h2></td>'
    IMG = '''<img src={0} >'''
    tbl = []
    tbl.append (
           TR.format(
               TH.format(content='Topic',bgcolor=header_bgcolor)+
               TH.format(content='Word Cloud',bgcolor=header_bgcolor)+
               TH.format(content='No. Words', bgcolor=header_bgcolor)
           )
    )    

    topics_sorted = sorted([int(k) for k in topic_cloud_dict.keys()])

    for topic_num in topics_sorted:
        num_words = len(topic_cloud_dict[str(topic_num)]['word_freq_list'])
        tbl.append(
            TR.format(
                   TD.format(content=topic_num,bgcolor=cell_bgcolor)+
                   TD_WITH_ID.format(id=topic_cloud_dict[str(topic_num)]['id'],content='',bgcolor=cell_bgcolor)+
                   TD.format(content=num_words,bgcolor=cell_bgcolor)
            )
        )

    response_dict = { "topic_cloud_d3":topic_cloud_dict, "topic_cloud_d3_table":TABLE.format('\n'.join(tbl)) }

    return HttpResponse(json.dumps(response_dict),content_type='application/json')
    

def unexpectedErrorMessage(msg):
    '''
       Return HTML message displaying unexpected error occurred
    '''
    uError = '''<div style="padding-left:150px">
                    <div><img src='/stat/images/error.png' height="100" width="100" style="padding-left:200px"></div>
                    <div><font size="4"  color="red">{0}</font></div>
                </div>
    '''.format(msg)
    return HttpResponse(uError)