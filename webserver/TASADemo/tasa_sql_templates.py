# -*- coding: utf-8 -*-
'''
  Srivatsan Ramanujam <sramanujam@gopivotal.com>
  Jarrod Vawdrey <jvawdrey@gopivotal.com>
  NLP Demo SQL templates
'''

def getTop20RelevantTweetsSQL(search_term):
    '''
       Top 20 Relevant Tweets (by score descending)
       Columns: displayname, preferredusername, body, image
    '''
    sql = '''
             SELECT displayname,
                    preferredusername,
                    body,
                    image
             FROM
             (
                    SELECT t3.displayname,
                           t3.preferredusername,
                           t2.body,
                           t3.image,
                           row_number() OVER (ORDER BY score DESC) AS _n_
                    FROM gptext.search(
                                TABLE(SELECT 1 SCATTER BY 1), 
                                'vatsandb.topicdemo.tweet_dataset',
                                '{search_term}',
                                null,
                                'score desc') AS t1,
                         topicdemo.tweet_dataset AS t2,
                         sentimentdemo.actor_info AS t3
                    WHERE t1.id=t2.id AND t2.tweet_id=t3.tweet_id
             ) foo
             WHERE _n_ <= 20
             ORDER BY _n_
          '''
    return sql.format(search_term=search_term)


def getTop20RelevantTweetsRangeSQL(search_term,min_timestamp,max_timestamp):
    '''
       Top 20 Relevant Tweets (by score descending) for a given date range
       min_timestamp and max_timestamp to be of format: YYYY-MM-DDTHH:MM:SSZ (i.e. 2013-07-01T00:00:00Z)
       Columns: displayname, preferredusername, body, image
    '''
    sql = '''
             SELECT displayname,
                    preferredusername,
                    body,
                    image
             FROM
             (
                    SELECT t3.displayname,
                           t3.preferredusername,
                           t2.body,
                           t3.image,
                           row_number() OVER (ORDER BY score DESC) AS _n_
                    FROM gptext.search(
                                TABLE(SELECT 1 SCATTER BY 1), 
                                'vatsandb.topicdemo.tweet_dataset',
                                '{search_term}',
                                '{{postedtime:[{min_timestamp} TO {max_timestamp}]}}',
                                'score desc') AS t1,
                         topicdemo.tweet_dataset AS t2,
                         sentimentdemo.actor_info AS t3
                    WHERE t1.id=t2.id AND t2.tweet_id=t3.tweet_id
             ) foo
             WHERE _n_ <= 20
             ORDER BY _n_
          '''
    return sql.format(search_term=search_term, min_timestamp=min_timestamp, max_timestamp=max_timestamp)


def getTop20RelevantTweetsRangeSentSQL(search_term,min_timestamp,max_timestamp,sentiment):
    '''
       Top 20 Relevant Tweets (by score descending) for a given time range and sentiment
       min_timestamp and max_timestamp to be of format: YYYY-MM-DDTHH:MM:SSZ (i.e. 2013-07-01T00:00:00Z)
       sentiment: 'negative','positive', or 'neutral' 
       Columns: displayname, preferredusername, body, image
    '''
    sql = '''
             SELECT postedtime,
                    displayname,
                    preferredusername,
                    body,
                    image,
                    sentiment
             FROM
             (
	            SELECT *,
	                   row_number() OVER (PARTITION BY sentiment ORDER BY score DESC) AS _n_
	            FROM
	            (
		           SELECT t1.score,
		                  t2.postedtime,
		                  t3.displayname,
		                  t3.preferredusername,
		                  t2.body,
		                  t3.image,
		                  CASE WHEN t4.median_sentiment_index > 1 THEN 'positive'
		                       WHEN t4.median_sentiment_index < -1 THEN 'negative'
		                       WHEN t4.median_sentiment_index BETWEEN -1 AND 1 THEN 'neutral'
		                  END AS sentiment
		           FROM gptext.search(TABLE(SELECT 1 SCATTER BY 1), 
			                      'vatsandb.topicdemo.tweet_dataset',
			                      '{search_term}',
                                              '{{postedtime:[{min_timestamp} TO {max_timestamp}]}}',
			                      'score desc') AS t1,
		                topicdemo.tweet_dataset AS t2,
		                sentimentdemo.actor_info AS t3,
		                sentimentdemo.training_data_scored AS t4
		           WHERE t1.id=t2.id AND t2.tweet_id=t3.tweet_id AND t2.tweet_id = t4.id AND t4.median_sentiment_index NOTNULL
                    ) t5
            ) t6
            WHERE sentiment = '{sentiment}'
            AND _n_ <= 20
            ORDER BY score DESC
         '''
    return sql.format(search_term=search_term, min_timestamp=min_timestamp, max_timestamp=max_timestamp, sentiment=sentiment)
 

def getCountOfRelevantTweetsSQL(search_term):
    '''
       Grab the count of relevant tweets
    '''
    sql = '''
             SELECT * FROM gptext.search_count('vatsandb.topicdemo.tweet_dataset','{search_term}', null)
          '''
    return sql.format(search_term=search_term)


def getCountOfRelevantTweetsRangeSQL(search_term, min_timestamp, max_timestamp):
    '''
       Grab the count of relevant tweets within date range
       min_timestamp and max_timestamp to be of format: YYYY-MM-DDTHH:MM:SSZ (i.e. 2013-07-01T00:00:00Z) 
    '''
    sql = '''
             SELECT * FROM gptext.search_count('vatsandb.topicdemo.tweet_dataset','{search_term}','{{postedtime:[{min_timestamp} TO {max_timestamp}]}}')
          '''
    return sql.format(search_term=search_term,min_timestamp=min_timestamp,max_timestamp=max_timestamp)


def getStatsRelevantTweetsSQL(search_term,min_timestamp,max_timestamp):
    '''
       Grab count of relevant tweets, average median_sentiment_index, count of tweets for each sentiment label
       min_timestamp and max_timestamp to be of format: YYYY-MM-DDTHH:MM:SSZ (i.e. 2013-07-01T00:00:00Z)
    '''
    sql = '''
             SELECT count(tweet_id) as num_tweets,
                    avg(median_sentiment_index) as mean_sentiment_index,
                    count(tweet_id) FILTER (WHERE median_sentiment_index > 1) AS positive_count,
                    count(tweet_id) FILTER (WHERE median_sentiment_index < -1) AS negative_count,
                    count(tweet_id) FILTER (WHERE median_sentiment_index BETWEEN -1 AND 1) AS neutral_count
             FROM
             (
	            SELECT t1.*,
	                   t2.tweet_id,
	                   t2.postedtime,
	                   t3.median_sentiment_index
	            FROM gptext.search (
                             TABLE(SELECT 1 SCATTER BY 1),
	                     'vatsandb.topicdemo.tweet_dataset',
                             '{search_term}',
                             '{{postedtime:[{min_timestamp} TO {max_timestamp}]}}'
                           ) t1,
                         topicdemo.tweet_dataset t2,
                         sentimentdemo.training_data_scored t3
	            WHERE t1.id = t2.id AND t2.tweet_id = t3.id AND t3.median_sentiment_index NOTNULL
             ) q
          '''
    return sql.format(search_term=search_term, min_timestamp=min_timestamp, max_timestamp=max_timestamp)