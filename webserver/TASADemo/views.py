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
from webserver.common.time_series_sql_template import *
from webserver.GPSentiDemo.sentiment_sql_templates import *
from webserver.GPTopicDemo.views import topicDashboardGenerator

SEARCH_TERM = 'sr_trm'
SEARCH_ADJECTIVE = 'sr_adj'
TIMESTAMP = 'ts'
SENTIMENT = 'snt'
HEATMAP = 'hmap'
TOPICS = 'num_topics'

conn = DBConnect()

@csrf_exempt
def top_tweets(request):
    search_term = request.REQUEST.get(SEARCH_TERM)
    search_adjective = request.REQUEST.get(SEARCH_ADJECTIVE)

    if search_adjective:
        search_term = '(%s AND %s)' % (search_term, search_adjective)

    tweet_sql = getTop20RelevantTweetsSQL(search_term)
    count_sql = getCountOfRelevantTweetsSQL(search_term)

    _, tweets = conn.fetchRows(tweet_sql)
    _, counts = conn.fetchRows(count_sql)

    result = {
        'tweets': {'total': [{'username': tweet[1], 'text': tweet[2]} for tweet in tweets]},
        'counts': {'total': counts[0][0]}
    }

    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def total_tweets(request):
    search_term = request.REQUEST[SEARCH_TERM]

    _, time_series = conn.fetchRows(numTweetsByDate(search_term))
    _, tweet_ids_by_date = conn.fetchRows(getTopTweetIdsSQL(search_term))
    _, tweets_by_id = conn.fetchRows(getTopTweetDataSQL(search_term))

    tweet_ids_by_date = {r.get('posted_date'): r.get('tweet_ids') for r in tweet_ids_by_date}
    tweets_by_id = {r['id']: {'username': r['preferredusername'], 'text': r['body']} for r in tweets_by_id}

    result = [
        {'posted_date': calendar.timegm(point['posted_date'].timetuple()) * 1000,
         'tweets': {'total': [tweets_by_id[tweet_id] for tweet_id in tweet_ids_by_date[point['posted_date']] if tweet_id in tweets_by_id]},
         'counts': {'total': point['num_tweets']}}
        for point in sorted(time_series, key=itemgetter('posted_date'))
    ]
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def sentiment_mapping(request):
    search_term = request.REQUEST[SEARCH_TERM]

    _, time_series = conn.fetchRows(getMultiSeriesSentimentSQl(search_term))
    _, raw_tweet_ids_by_date = conn.fetchRows(getTopTweetIdsWithSentimentSQL(search_term))
    _, tweets_by_id = conn.fetchRows(getTopTweetDataWithSentimentSQL(search_term))

    tweet_ids_by_date = collections.defaultdict(lambda: {})
    for r in raw_tweet_ids_by_date:
        tweet_ids_by_date[r['posted_date']][r['sentiment']] = r.get('tweet_ids')

    tweets_by_id = {r['id']: {'username': r['preferredusername'], 'text': r['body']} for r in tweets_by_id}

    result = [
        {
            'posted_date': calendar.timegm(point['posted_date'].timetuple()) * 1000,
            'tweets': {
                'positive': [tweets_by_id[tweet_id] for tweet_id in tweet_ids_by_date[point['posted_date']].get('positive', []) if tweet_id in tweets_by_id],
                'negative': [tweets_by_id[tweet_id] for tweet_id in tweet_ids_by_date[point['posted_date']].get('negative', []) if tweet_id in tweets_by_id],
                'neutral': [tweets_by_id[tweet_id] for tweet_id in tweet_ids_by_date[point['posted_date']].get('neutral', []) if tweet_id in tweets_by_id]
            },
            'counts': {
                'total': point['positive_count'] + point['negative_count'] + point['neutral_count'],
                'positive': point['positive_count'],
                'negative': point['negative_count'],
                'neutral': point['neutral_count']
            }
        }
        for point in sorted(time_series, key=itemgetter('posted_date'))
    ]

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def tweet_activity(request):
    search_term = request.REQUEST[SEARCH_TERM]

    _, tweet_ids_by_date = conn.fetchRows(getHeatMapTweetIdsSQL(search_term))
    _, tweets_by_id = conn.fetchRows(getHeatMapTweetDateSQL(search_term))

    tweets_by_id = {r['id']: {'username': r['preferredusername'], 'text': r['body']} for r in tweets_by_id}

    result = collections.defaultdict(lambda: {'tweets': {}})
    for row in tweet_ids_by_date:
        point = result[(row['day_of_week'], row['hour_of_day'])]
        point['day'] = row['day_of_week']
        point['hour'] = row['hour_of_day']
        point['tweets'][row['sentiment']] = [tweets_by_id[tweet_id] for tweet_id in row.get('id_arr', []) if tweet_id in tweets_by_id]
        point['counts'] = {'total': row.get('num_tweets', 0),
                           'positive': row.get('num_positive', 0),
                           'negative': row.get('num_negative', 0),
                           'neutral': row.get('num_tweets', 0) - row.get('num_positive', 0) - row.get('num_negative', 0)}
    result = result.values()

    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def adjectives(request):
    search_term = request.REQUEST[SEARCH_TERM]

    _, tweet_ids_by_adjective = conn.fetchRows(getAdjectivesTweetIdsSQL(search_term))
    _, tweets_by_id = conn.fetchRows(getAdjectivesTweetDataSQL(search_term))

    tweets_by_id = {r['id']: {'username': r['preferredusername'], 'text': r['body']} for r in tweets_by_id}
    result = [{'word': r['token'],
               'normalized_frequency': float(r['normalized_frequency']),
               'tweets': {'total': [tweets_by_id[tweet_id] for tweet_id in r['id_arr'] if tweet_id in tweets_by_id]}}
              for r in tweet_ids_by_adjective]

    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def topic_cluster(request):
    search_term = request.REQUEST[SEARCH_TERM]
    topics = request.REQUEST[TOPICS]

    result = topicDashboardGenerator(search_term, topics)

    return HttpResponse(json.dumps(result), content_type='application/json')
