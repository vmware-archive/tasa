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
    search_term = request.REQUEST.get(SEARCH_TERM)
    timestamp = request.REQUEST.get(TIMESTAMP)
    sentiment = request.REQUEST.get(SENTIMENT)

    if timestamp:
        timestamp = datetime.date.fromtimestamp(int(timestamp) / 1000)
        min_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        max_timestamp = (timestamp + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    if timestamp and sentiment:
        tweet_sql = getTop20RelevantTweetsRangeSentSQL(search_term, min_timestamp, max_timestamp, sentiment)
        count_sql = getStatsRelevantTweetsSQL(search_term, min_timestamp, max_timestamp)
    elif timestamp:
        tweet_sql = getTop20RelevantTweetsRangeSQL(search_term, min_timestamp, max_timestamp)
        count_sql = getCountOfRelevantTweetsRangeSQL(search_term, min_timestamp, max_timestamp)
    else:
        tweet_sql = getTop20RelevantTweetsSQL(search_term)
        count_sql = getCountOfRelevantTweetsSQL(search_term)

    _, tweet_rows = conn.fetchRows(tweet_sql)
    _, count_rows = conn.fetchRows(count_sql)

    tweets = [{'display_name': tweet[0], 'username': tweet[1], 'text': tweet[2], 'profile_image': tweet[3]} for tweet in tweet_rows]
    counts = dict(zip(('total', 'mean_sentiment_index', 'positive', 'negative', 'neutral'), count_rows[0]))

    return HttpResponse(json.dumps({'tweets': tweets, 'counts': counts}), content_type='application/json')