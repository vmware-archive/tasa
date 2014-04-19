# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pkg_resources import resource_string
from webserver.settings import MEDIA_ROOT
import psycopg2
import os, json, time, datetime
from operator import itemgetter
from webserver.common.dbconnector import DBConnect
from webserver.TASADemo.tasa_sql_templates import *

SEARCH_TERM = 'sr_trm'
TIMESTAMP = 'ts'
SENTIMENT = 'snt'

conn = DBConnect()

@csrf_exempt
def relevant_tweets(request):
    search_term = request.REQUEST[SEARCH_TERM]

    sql = getTop20RelevantTweetsSQL(search_term)
    _, rows = conn.fetchRows(sql)

    tweets = [{'display_name': tweet[0], 'username': tweet[1], 'text': tweet[2], 'profile_image': tweet[3]} for tweet in rows]
    print(tweets)

    _, count = conn.fetchRows(getCountOfRelevantTweetsSQL(search_term))
    print("Count: ", count[0][0])

    response = {
        "tweets": tweets,
        'count': count[0][0]
    }

    return HttpResponse(json.dumps(response), content_type='application/json')

def relevant_tweets_for_day(request):
    search_term = request.REQUEST[SEARCH_TERM]
    timestamp = datetime.date.fromtimestamp(int(request.REQUEST[TIMESTAMP]) / 1000)

    print(search_term, timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), (timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    sql = getTop20RelevantTweetsRangeSQL(search_term, timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), (timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    _, rows = conn.fetchRows(sql)

    tweets = [{'display_name': tweet[0], 'username': tweet[1], 'text': tweet[2], 'profile_image': tweet[3]} for tweet in rows]
    print(tweets)

    return HttpResponse(json.dumps(tweets), content_type='application/json')


def relevant_tweets_for_day_and_sentiment(request):
    search_term = request.REQUEST[SEARCH_TERM]
    timestamp = datetime.date.fromtimestamp(int(request.REQUEST[TIMESTAMP]) / 1000)
    sentiment = request.REQUEST[SENTIMENT]

    print(search_term,
          timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
          (timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
          sentiment
    )
    sql = getTop20RelevantTweetsRangeSentSQL(search_term,
                                             timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             (timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             sentiment
    )
    _, rows = conn.fetchRows(sql)

    tweets = [{'display_name': tweet[1], 'username': tweet[2], 'text': tweet[3], 'profile_image': tweet[4]} for tweet in rows]
    print(tweets)

    return HttpResponse(json.dumps(tweets), content_type='application/json')