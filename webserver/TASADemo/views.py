# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pkg_resources import resource_string
from webserver.settings import MEDIA_ROOT
import psycopg2
import os, json, time, datetime, calendar, collections
from operator import itemgetter
from webserver.common.dbconnector import DBConnect
from webserver.TASADemo.tasa_sql_templates import *

SEARCH_TERM = 'sr_trm'
SEARCH_ADJECTIVE = 'sr_adj'
TIMESTAMP = 'ts'
SENTIMENT = 'snt'
HEATMAP = 'hmap'

conn = DBConnect()

@csrf_exempt
def relevant_tweets(request):
    search_term = request.REQUEST.get(SEARCH_TERM)
    search_adjective = request.REQUEST.get(SEARCH_ADJECTIVE)
    timestamp = request.REQUEST.get(TIMESTAMP)
    sentiment = request.REQUEST.get(SENTIMENT)

    if search_adjective:
        search_term = '(%s AND %s)' % (search_term, search_adjective)

    if timestamp:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp) / 1000 + time.localtime().tm_isdst * 60 * 60)
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

@csrf_exempt
def tweets(request):
    search_term = request.REQUEST.get(SEARCH_TERM)
    sentiment = request.REQUEST.get(SENTIMENT)
    heatmap = request.REQUEST.get(HEATMAP)

    if sentiment:
        _, raw_tweet_ids_by_date = conn.fetchRows(getTopTweetIdsWithSentimentSQL(search_term))
        _, tweets_by_id = conn.fetchRows(getTopTweetDataWithSentimentSQL(search_term))

        tweet_ids_by_date = collections.defaultdict(lambda: {})
        for row in raw_tweet_ids_by_date:
            tweet_ids_by_date[str(calendar.timegm(row.get('posted_date').timetuple()) * 1000)][row.get('sentiment')] = row.get('tweet_ids')

        tweets_by_id = dict([(str(r.get('id')), {'username': r.get('preferredusername'), 'text': r.get('body')}) for r in tweets_by_id])
    elif heatmap:
        _, raw_tweet_ids_by_date = conn.fetchRows(getHeatMapTweetIdsSQL(search_term))
        _, tweets_by_id = conn.fetchRows(getHeatMapTweetDateSQL(search_term))

        less_raw_tweet_ids_by_date = collections.defaultdict(lambda: collections.defaultdict(lambda: {'tweets': {'positive': [], 'negative': []}, 'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}}))
        for row in raw_tweet_ids_by_date:
            less_raw_tweet_ids_by_date[row.get('day_of_week')][row.get('hour_of_day')]['tweets'][row.get('sentiment')] = row.get('id_arr', [])
            less_raw_tweet_ids_by_date[row.get('day_of_week')][row.get('hour_of_day')]['counts'] = {'total': row.get('num_tweets', 0),
                                                                                                    'positive': row.get('num_positive', 0),
                                                                                                    'negative': row.get('num_negative', 0),
                                                                                                    'neutral': row.get('num_neutral', 0)}
        tweet_ids_by_date = []
        for day in less_raw_tweet_ids_by_date:
            for hour in less_raw_tweet_ids_by_date[day]:
                data = less_raw_tweet_ids_by_date[day][hour]
                tweet_ids_by_date.append({'day': day, 'hour': hour, 'tweets': data['tweets'], 'counts': data['counts']})


        tweets_by_id = dict([(str(r.get('id')), {'username': r.get('preferredusername'), 'text': r.get('body')}) for r in tweets_by_id])
    else:
        _, tweet_ids_by_date = conn.fetchRows(getTopTweetIdsSQL(search_term))
        _, tweets_by_id = conn.fetchRows(getTopTweetDataSQL(search_term))

        tweet_ids_by_date = dict([(str(calendar.timegm(r.get('posted_date').timetuple()) * 1000), r.get('tweet_ids')) for r in tweet_ids_by_date])
        tweets_by_id = dict([(str(r.get('id')), {'username': r.get('preferredusername'), 'text': r.get('body')}) for r in tweets_by_id])

    return HttpResponse(json.dumps({'tweet_ids_by_date': tweet_ids_by_date, 'tweets_by_id': tweets_by_id}), content_type='application/json')