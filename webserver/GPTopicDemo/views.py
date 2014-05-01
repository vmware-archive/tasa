# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pkg_resources import resource_string
from webserver.settings import MEDIA_ROOT
import psycopg2
import os,json,time,datetime,calendar
from operator import itemgetter
#Webserver module imports
from webserver.common.dbconnector import DBConnect
from webserver.GPTopicDemo.topic_modeling_sql_template import *
from webserver.GPTopicDemo.topic_cloud_gen import *
from webserver.common.time_series_sql_template import *

SEARCH_TERM = 'sr_trm'
NUM_TOPICS = 'num_topics'
TOPIC_HTML_FORM = resource_string('webserver.common.resources.html','topic_input_page.html').encode('utf-8')

conn = DBConnect()

@csrf_exempt
def topic_home(request):
    '''Handles request that comes from a webpage (where a form is displayed for the user to enter the opinion string'''
    return HttpResponse(TOPIC_HTML_FORM)

@csrf_exempt
def tweets_over_time(request):
    ''' Return the number of tweets matching the search query for each date'''
    search_term = request.REQUEST[SEARCH_TERM]
    suffix_id = str(time.time())
    sql = numTweetsByDate(search_term, suffix_id)
    executionStatus, rows = conn.fetchRows(sql)
    dt_count_lst = [(r.get('posted_date'),r.get('num_tweets')) for r in rows]
    dt_count_lst = sorted(dt_count_lst,key=itemgetter(0),reverse=True)
    dt_count_dict = {'tseries':[{'posted_date':calendar.timegm(elem[0].timetuple())*1000,'num_tweets':elem[1]} for elem in dt_count_lst]}
    print 'dt_count_lst:\n','\n'.join(['\t'.join([str(elem[0]),str(elem[1])]) for elem in dt_count_lst])
    return HttpResponse(json.dumps(dt_count_dict),content_type='application/json')

def augmentedTweet(body,topic):
    '''
       Add the topic identifier to the tweet body
    '''
    return u'{body}'.format(body=body,topic=str(topic))

def topic_graph_generator(suffix_id, num_topics):
    '''
       Generate a topic graph based on the results of the topic model.
       This will be displayed as a force-directed graph usin D3.js
    '''
    sql = getTopicGraphQuery(suffix_id, num_topics,'rank')
    #print 'Topic Graph Query:',sql

    executionStatus, rows = conn.fetchRows(sql) 
    nodes = {} 
    edges = []
    topic_graph={}
    for r in rows:
        tweet_i = r.get('tweet_i')
        tweet_i_body = r.get('tweet_i_body')
        tweet_j = r.get('tweet_j')
        tweet_j_body = r.get('tweet_j_body')
        label = r.get('label')
        edge_weight = r.get('edge_weight')
        #Add the nodes to the nodes dict
        nodes[tweet_i]={'name':augmentedTweet(tweet_i_body,label),'group':label}        
        nodes[tweet_j]={'name':augmentedTweet(tweet_j_body,label),'group':label} 
        #Add edges to the edges list
        edges.append([tweet_i,tweet_j,edge_weight])

    #Sort the nodes by id and give each node an index
    nodes_sorted = sorted(nodes.keys())
    node_indices = dict((nodes_sorted[i],i) for i in range(len(nodes_sorted)))
    #Generate the topic graph in JSON
    topic_graph['nodes'] = [nodes[nd_id] for nd_id in nodes_sorted]
    topic_graph['links'] = [{'source':node_indices[ed[0]], 'target':node_indices[ed[1]],'value':ed[2]} for ed in edges] 
    
    #Create a topic dict to list the number of tweets in a given topic 
    topic_dict = {}
    topic_dict_sql = getNumTweetsPerTopic(suffix_id, num_topics)
    executionStatus, rows = conn.fetchRows(topic_dict_sql)
    for r in rows:
        topic_dict[r.get('label')]=r.get('num_tweets')

    return json.dumps(topic_graph),topic_dict     

def fetchTopicResultsList(suffix_id, num_topics):
    '''
       Fetch a list of the form [[topic_num, num_tweets, [word1, word2, word3....]], [topic_num, num_tweets, [word1, word2, word3....]]]
    '''
    topic_results_list = []
    topic_results_list_sql = getTopicResults(suffix_id, num_topics)
    executionStatus, rows = conn.fetchRows(topic_results_list_sql)
    for r in rows:
        topic_results_list.append([r.get('topic_num'), r.get('word_count'), r.get('word_allocs')])

    return topic_results_list

@csrf_exempt
def topic_fetch(request):
    ''' Handles creation of a topic dashboard '''
    search_term = request.REQUEST[SEARCH_TERM]
    num_topics = request.REQUEST[NUM_TOPICS]
    print '#Request search_term : ',search_term, ' num topics: ',num_topics
    
    return topicDashboardGenerator(search_term,num_topics)

def topicDashboardGenerator(search_term, num_topics):
    ''' This function should be invoked in a new thread '''

    suffix_id = str(time.time()).replace('.', '_dot_')

    conn_dict = DBConnect.getConnectionString()

    #0) Retrieve matching tweets for the search term
    print 'Retrieving matching tweets'
    executionStatus = conn.executeQuery(retrieveMatchingTweets(search_term,suffix_id))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)

    #1) Count number of matching tweets, if there were none, display an error and return
    sql = countOfMatchingTweets(search_term, suffix_id)
    executionStatus, rows = conn.fetchRows(sql) 
    numMatchingTweets = rows[0]['num_matching_tweets'] if rows else -1    
    print 'Matching tweets: ',numMatchingTweets

    if(executionStatus or numMatchingTweets==0):
        cleanUp(suffix_id, num_topics)
        if(numMatchingTweets==0):
            executionStatus = 'Sorry. Your search did not match any tweets in our database.'
        return unexpectedErrorMessage(executionStatus)

    #2) Prepare dataset to run topic analysis on
    print 'Preparing dataset for topic analysis'
    executionStatus = conn.executeQuery(prepareDatasetForLDA(search_term,suffix_id))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)
    
    #3) Run the LDA topic model
    print 'Running topic model (LDA)'
    executionStatus = conn.executeQuery(runLDAModel(suffix_id,num_topics))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)

    #4) Extract the topic assignments
    print 'Exporting topic assignments'
    executionStatus = conn.executeQuery(exportTopicAssignments(suffix_id,num_topics))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)

    #5) Generate topic graph
    print 'Generating topic graph'
    topic_graph_sql = generateTopicGraph(search_term, suffix_id,num_topics)

    executionStatus = conn.executeQuery(topic_graph_sql)
    if(executionStatus):
        print 'Execution status: ',executionStatus
        cleanUp(suffix_id, num_topics)
        return unexpectedErrorMessage(executionStatus)

    print 'Building topic graph JSON'    
    topic_graph, topic_dict = topic_graph_generator(suffix_id, num_topics)

    #6) Return the topic_graph and the topic_cloud, both of which will be rendered through D3 on the client.
    print 'Generating topic clouds'

    topic_cloud = '''<div> 
                       <div>
                            <h2 style="color:blue;padding-left:200px">Your search matched {numMatchingTweets} tweets in our database.</h2>
                       </div>
                       <div>
                            {topic_table}
                       </div>
                  </div>
               '''

    topic_cloud_dict = createTopicCloudDict(fetchTopicResultsList(suffix_id, num_topics))

    #7) Topic Drill Down
    tweetid_to_body_dict, topic_drilldown_dict = getTopicCloudDrillDown(search_term, suffix_id, num_topics)


    #8) Clean-up
    cleanUp(suffix_id,num_topics)

    topics_response_dict = {
                            "topic_graph":topic_graph,
                            "topic_cloud_d3":topic_cloud_dict,
                            "topic_cloud_d3_table":createTopicCloudTableD3(topic_cloud_dict,topic_dict),
                            "tweetid_to_body_dict":tweetid_to_body_dict,
                            "topic_drilldown_dict":topic_drilldown_dict
                           }

    return HttpResponse(json.dumps(topics_response_dict),content_type='application/json')


def cleanUp(suffix_id, num_topics):
    '''
       Remove any tables generated in the process
    '''
    print 'Cleaning up'
    executionStatus = conn.executeQuery(getCleanUpQuery(suffix_id,num_topics))
    if(executionStatus):
        print 'Clean-up error: ',executionStatus

def createTopicCloudDict(topic_word_mappings):
    '''
       Generate D3.js Word Clouds to display the contents of the topic
    '''
    TOPIC_CLOUD_PREFIX = 'topic_cloud_{topic_num}'
    #topic_word_mappings is of the form [topic_num, num_words, {words as a list}]
    #topic_word_mappings = parseFile(topic_results_file_local,{})
    topic_word_mappings = filterTopOverlappingTokens(10,topic_word_mappings)
    topic_cloud_dict = {}
    for triplet in topic_word_mappings:
        topic_num = triplet[0]
        num_words = triplet[1]
        word_list = triplet[2]
        word_count_dict = {}
        for w in word_list:
            if word_count_dict.has_key(w):
                word_count_dict[w] += 1
            else: 
                word_count_dict[w] = 1
        #Normalize frequency counts as a ratio of the token with maximum frequency in this topic
        max_freq = max(word_count_dict.values())
        word_count_dict = dict([(k,v*1.0/max_freq) for k,v in word_count_dict.items()])
        word_count_list = [{"word":key,"normalized_frequency":word_count_dict[key]} for key in word_count_dict.keys()]
        topic_cloud_dict[topic_num]={'id':TOPIC_CLOUD_PREFIX.format(topic_num=topic_num),'word_freq_list':word_count_list}

    return topic_cloud_dict    

def createTopicCloudTableD3(topic_cloud_dict,topic_dict):
    ''' Creates an HTML with the topic cloud field empty. The javascript in D3.js front-end will render a word cloud in the topic cloud fields '''
    header_bgcolor="#2E8B57"
    cell_bgcolor='white'
    TABLE = '<table style="border:1; border-collapse:collapse;padding:3px" width="800">{0}</table>'
    TR = '<tr>{0}</tr>'
    TD = '<td style="border:1px solid black;" bgcolor={bgcolor}><h3 align="center">{content}</h3></td>'
    TD_WITH_ID = '<td id="{id}" style="border:1px solid black;" bgcolor={bgcolor}><h3 align="center">{content}</h3></td>'
    TH = '<td style="border:1px solid black;" bgcolor={bgcolor}><h2 align="center">{content}</h2></td>'
    IMG = '''<img src={0} >'''
    tbl = []
    tbl.append(
           TR.format(
               TH.format(content='Topic',bgcolor=header_bgcolor)+
               TH.format(content='Word Cloud',bgcolor=header_bgcolor)+
               TH.format(content='#Tweets',bgcolor=header_bgcolor)
           )
    )    

    topics_sorted = sorted([int(k) for k,v in topic_cloud_dict.items()])

    for topic_num in topics_sorted:
        num_tweets = str(topic_dict[topic_num]) if topic_dict.has_key(topic_num) else '0'
        tbl.append(
            TR.format(
                   TD.format(content=topic_num,bgcolor=cell_bgcolor)+
                   TD_WITH_ID.format(id=topic_cloud_dict[topic_num]['id'],content='',bgcolor=cell_bgcolor)+
                   TD.format(content=num_tweets,bgcolor=cell_bgcolor)
            )
        )
    return TABLE.format('\n'.join(tbl))

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

def getTopicCloudDrillDown(search_term, suffix_id, num_topics):
    '''
        Provide drill-down capabilities for the topic cloud
    '''
    topic_drilldown_dict = {}
    tweetid_to_body_dict = {}

    #Step-1: Construct a tweetid_to_tweet_body dict, which holds the values for the top-1000 tweets for the given search term.
    executionStatus, rows = conn.fetchRows(getTweetIdToBodyDictQuery(search_term))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)

    for r in rows:
        tweetid_to_body_dict[r.get('id')]={'score':r.get('score'),'text':r.get('body'), 'username':r.get('preferredusername')}

    #Step-2: Return dict of the form {word: {topic_num: [tweetid_rank1, tweetid_rank2, ...]}}
    executionStatus, rows = conn.fetchRows(getTopicDrilldownDictQuery(search_term, suffix_id, num_topics))
    if(executionStatus):
        print 'Execution Status: ',executionStatus
        cleanUp(suffix_id,num_topics)
        return unexpectedErrorMessage(executionStatus)

    for r in rows:
        #Each row is a tuple of the form ['word','topic_num','id','rank']
        word = r.get('word')
        topic_num = r.get('topic_num')
        id = r.get('id')
        rank = r.get('rank')
        if(topic_drilldown_dict.has_key(word)):
            if(topic_drilldown_dict[word].has_key(topic_num)):
                topic_drilldown_dict[word][topic_num].append(id)
            else:
                topic_drilldown_dict[word][topic_num]=[id]
        else:
            topic_drilldown_dict[word]={topic_num:[id]}

    return (tweetid_to_body_dict, topic_drilldown_dict)
