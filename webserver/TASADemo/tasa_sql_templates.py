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


def getTopTweetIdsSQL(search_term):
    return '''
        select posted_date, array_agg(id) as tweet_ids
        from (
            select t1.id,
                   t1.score,
                   (t2.postedtime at time zone 'UTC')::date as posted_date,
                   row_number() over (partition by (t2.postedtime at time zone 'UTC')::date order by score desc) as index
            from gptext.search(
                     TABLE(select * from topicdemo.tweet_dataset),
                     'vatsandb.topicdemo.tweet_dataset',
                     '{search_term}',
                     null
                 ) t1,
                 topicdemo.tweet_dataset t2
            where t1.id = t2.id
        ) search
        where index <= 20
        group by posted_date
    '''.format(search_term=search_term)

def getTopTweetDataSQL(search_term):
    return '''
        	with id_to_attributes_map
        	as
        	(
        		select t1.id,
        		       t3.displayname,
        		       t3.preferredusername,
        		       t2.body,
        		       t3.image
        		from gptext.search(
        			     TABLE(select * from topicdemo.tweet_dataset),
        			     'vatsandb.topicdemo.tweet_dataset',
        			     '{search_term}',
        			     null
        		     ) t1,
        		     topicdemo.tweet_dataset t2,
        		     sentimentdemo.actor_info t3
        		where t1.id = t2.id and
        		      t2.tweet_id = t3.tweet_id
            )
            select id_to_attributes_map.*
            from
            (
        		select id
        		from
        		(
                    select t1.id,
                           t1.score,
                           (t2.postedtime at time zone 'UTC')::date as posted_date,
                           row_number() over (partition by (t2.postedtime at time zone 'UTC')::date order by score desc) as index
                    from gptext.search(
                             TABLE(select * from topicdemo.tweet_dataset),
                             'vatsandb.topicdemo.tweet_dataset',
                             '{search_term}',
                             null
                         ) t1,
                         topicdemo.tweet_dataset t2
                    where t1.id = t2.id
        		)q
        		where index <= 20
                group by id
    	    ) tbl1,
    	    id_to_attributes_map
    	    where tbl1.id = id_to_attributes_map.id
    '''.format(search_term=search_term)


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
             SELECT displayname,
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


def getTopTweetIdsWithSentimentSQL(search_term):
    return '''
        select posted_date,
               sentiment,
               array_agg(id) as tweet_ids
        from (
            select id,
                   score,
                   row_number() over(partition by posted_date, sentiment order by score desc) as index,
                   posted_date,
                   sentiment
            from (
                select t1.id,
    	               t1.score,
                       (t2.postedtime at time zone 'UTC')::date as posted_date,
                       case when t3.median_sentiment_index > 1 then 'positive'
    		                when t3.median_sentiment_index < -1 then 'negative'
    		                else 'neutral'
    	               end as sentiment
                from
                    gptext.search(
      			        TABLE(select * from topicdemo.tweet_dataset),
      			        'vatsandb.topicdemo.tweet_dataset',
      			        '{search_term}',
      			        null
    	            ) t1,
                    topicdemo.tweet_dataset t2,
                    sentimentdemo.training_data_scored t3
                where t1.id = t2.id and t2.tweet_id = t3.id and t3.median_sentiment_index IS NOT NULL
            ) q1
        ) q2
        where index <= 20
        group by posted_date, sentiment
    '''.format(search_term=search_term)

def getTopTweetDataWithSentimentSQL(search_term):
    return '''
        with id_to_attributes_map
        as (
            select t1.id,
                   t3.displayname,
                   t3.preferredusername,
                   t2.body,
                   t3.image
            from
                gptext.search(
                    TABLE(select * from topicdemo.tweet_dataset),
                    'vatsandb.topicdemo.tweet_dataset',
                    '{search_term}',
                    null
                ) t1,
                topicdemo.tweet_dataset t2,
                sentimentdemo.actor_info t3
            where t1.id = t2.id and t2.tweet_id = t3.tweet_id
        )
        select id_to_attributes_map.*
        from (
            select id
            from (
                select id,
                       score,
                       row_number() over(partition by posted_date, sentiment order by score desc) as index,
                       posted_date,
                       sentiment
                from (
                    select t1.id,
                           t1.score,
                           (t2.postedtime at time zone 'UTC')::date as posted_date,
                           case when t3.median_sentiment_index > 1 then 'positive'
                                when t3.median_sentiment_index < -1 then 'negative'
                                else 'neutral'
                           end as sentiment
                    from
                        gptext.search(
                            TABLE(select * from topicdemo.tweet_dataset),
                            'vatsandb.topicdemo.tweet_dataset',
                            '{search_term}',
                            null
                        ) t1,
                        topicdemo.tweet_dataset t2,
                        sentimentdemo.training_data_scored t3
                    where t1.id = t2.id and t2.tweet_id = t3.id and t3.median_sentiment_index IS NOT NULL
                ) q1
            ) q2
            where index <= 20
            group by id
        ) tbl1,
        id_to_attributes_map
        where tbl1.id = id_to_attributes_map.id
    '''.format(search_term=search_term)

def getHeatMapTweetIdsSQL(search_term):
    return '''
        with hmap
        as (
            select day_of_week,
                   hour_of_day,
                   id,
                   sentiment,
                   row_number() over (partition by day_of_week, hour_of_day, sentiment order by score desc) as index
            from
            (
                select t1.id,
                       t1.score,
                       case
                            when t3.median_sentiment_index > 1 then 'positive'
                            when t3.median_sentiment_index < -1 then 'negative'
                            else  'neutral'
                       end as sentiment,
                       extract(DOW from (t2.postedtime at time zone 'UTC')) as day_of_week,
                       extract(HOUR from (t2.postedtime at time zone 'UTC')) as hour_of_day
                from
                    gptext.search (
                        TABLE(select * from topicdemo.tweet_dataset),
                        'vatsandb.topicdemo.tweet_dataset',
                        '{search_term}',
                        null
                    ) t1,
                    topicdemo.tweet_dataset t2,
                    sentimentdemo.training_data_scored t3
                where t1.id = t2.id and t2.tweet_id = t3.id and t3.median_sentiment_index IS NOT NULL
            ) q
        )     
        select hmap_stats.day_of_week,
               hmap_stats.hour_of_day,
               id_arr.sentiment,
               hmap_stats.num_tweets,
               hmap_stats.num_positive,
               hmap_stats.num_negative,
               id_arr.id_arr
        from (
            select day_of_week,
                   hour_of_day,
                   count(id) as num_tweets,
                   count(id) filter(where sentiment='positive') as num_positive,
                   count(id) filter(where sentiment='negative') as num_negative,
                   count(id) filter(where sentiment='neutral') as num_neutral
            from hmap
            group by day_of_week, hour_of_day
        ) hmap_stats,
        (
            select day_of_week,
                   hour_of_day,
                   sentiment,
                   array_agg(id order by index) as id_arr
            from hmap
            where sentiment in ('positive', 'negative') and index <=10
            group by day_of_week, hour_of_day, sentiment
        ) id_arr
        where hmap_stats.day_of_week = id_arr.day_of_week and
        hmap_stats.hour_of_day = id_arr.hour_of_day
    '''.format(search_term=search_term)

def getHeatMapTweetDateSQL(search_term):
    return '''
        with hmap
        as (
            select day_of_week,
                   hour_of_day,
                   id,
                   sentiment,
                   row_number() over (partition by day_of_week, hour_of_day, sentiment order by score desc) as index
            from (
                select t1.id,
                       t1.score,
                       case
                           when t3.median_sentiment_index > 1 then 'positive'
                           when t3.median_sentiment_index < -1 then 'negative'
                           else  'neutral'
                       end as sentiment,
                       extract(DOW from (t2.postedtime at time zone 'UTC')) as day_of_week,
                       extract(HOUR from (t2.postedtime at time zone 'UTC')) as hour_of_day
                from
                    gptext.search (
                        TABLE(select * from topicdemo.tweet_dataset),
                        'vatsandb.topicdemo.tweet_dataset',
                        '{search_term}',
                        null
                    ) t1,
                    topicdemo.tweet_dataset t2,
                    sentimentdemo.training_data_scored t3
                where t1.id = t2.id and t2.tweet_id = t3.id and t3.median_sentiment_index IS NOT NULL
            ) q
        ),
        id_to_attributes_map
        as (
            select t1.id,
                   t3.displayname,
                   t3.preferredusername,
                   t2.body,
                   t3.image
            from
                gptext.search(
                    TABLE(select * from topicdemo.tweet_dataset),
                    'vatsandb.topicdemo.tweet_dataset',
                    '{search_term}',
                    null
                ) t1,
                topicdemo.tweet_dataset t2,
                sentimentdemo.actor_info t3
            where t1.id = t2.id and t2.tweet_id = t3.tweet_id
        )
        select id_to_attributes_map.*
        from
            (
                select id
                from hmap
                where sentiment in ('positive', 'negative') and index <=10
                group by id
            ) tbl1,
            id_to_attributes_map
        where tbl1.id = id_to_attributes_map.id                     
    '''.format(search_term=search_term)

def getAdjectivesTweetIdsSQL(search_term):
    return '''
        	with token_freq_id_arr
        	as
        	(
        		select token,
        		       count(*) as frequency,
        		       array_agg(id order by score desc) as id_arr
        		from
        		(
        			select t1.id,
        			       t1.score,
        			       lower(t3.token) as token,
        			       t3.indx
        			from gptext.search(
        				TABLE(select * from topicdemo.tweet_dataset),
        				'vatsandb.topicdemo.tweet_dataset',
        				'{search_term}',
        				null
        			     ) t1,
        			     topicdemo.tweet_dataset t2,
        			     sentimentdemo.training_data_pos_tagged t3
        			     where t1.id = t2.id and t2.tweet_id = t3.id and t3.tag = 'A'
        		 ) tbl
        		 group by token
        	)
        	select token,
        	       frequency*1.0/(select max(frequency) from token_freq_id_arr) as normalized_frequency,
        	       id_arr[1:20] -- Top 20 tweets per adjective
        	from token_freq_id_arr
        	order by normalized_frequency desc
            --Top-100 adjectives by normalized frequency
        	limit 100
    '''.format(search_term=search_term)

def getAdjectivesTweetDataSQL(search_term):
    return '''
        	with id_to_attributes_map
        	as
        	(
        		select t1.id,
        		       t3.displayname,
        		       t3.preferredusername,
        		       t2.body,
        		       t3.image
        		from gptext.search(
        			     TABLE(select * from topicdemo.tweet_dataset),
        			     'vatsandb.topicdemo.tweet_dataset',
        			     '{search_term}',
        			     null
        		     ) t1,
        		     topicdemo.tweet_dataset t2,
        		     sentimentdemo.actor_info t3
        		where t1.id = t2.id and
        		      t2.tweet_id = t3.tweet_id
        	),
        	token_freq_id_arr
        	as
        	(
        		select token,
        		       count(*) as frequency,
        		       array_agg(id order by score desc) as id_arr
        		from
        		(
        			select t1.id,
        			       t1.score,
        			       lower(t3.token) as token,
        			       t3.indx
        			from gptext.search(
        				TABLE(select * from topicdemo.tweet_dataset),
        				'vatsandb.topicdemo.tweet_dataset',
        				'{search_term}',
        				null
        			     ) t1,
        			     topicdemo.tweet_dataset t2,
        			     sentimentdemo.training_data_pos_tagged t3
        			     where t1.id = t2.id and t2.tweet_id = t3.id and t3.tag = 'A'
        		 ) tbl
        		 group by token
                 order by frequency desc
                 -- Top-100 adjectives only
                 limit 100
        	)
        	select id_to_attributes_map.*
        	from
        	(
        		select id
        		from
        		(
        			select token,
        			       frequency,
                           -- Top-20 tweets per adjective
        			       unnest(id_arr[1:20]) as id
        			from token_freq_id_arr

        		)q
        		group by id
        	) top_adj,
        	id_to_attributes_map
        	where id_to_attributes_map.id = top_adj.id
    '''.format(search_term=search_term)

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