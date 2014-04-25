# -*- coding: utf-8 -*-
'''
  Srivatsan Ramanujam <sramanujam@gopivotal.com>
  Sentiment plots related SQL templates
'''
def getMultiSeriesSentimentSQl(search_term):
    '''
       Given the search term, query GPText Index to fetch sentiment plot
    '''
    sql = '''
             select posted_date,
             sum(positive) as positive_count,
             sum(negative) as negative_count,
             sum(neutral) as neutral_count
          from
          (
               select tweet_id,
                      (postedtime at time zone 'UTC')::date as posted_date,
                      case when median_sentiment_index > 1 then 1 else 0 end as positive,
                      case when median_sentiment_index < -1 then 1 else 0 end as negative,
                      case when median_sentiment_index between -1 and 1 then 1 else 0 end as neutral
               from
               (
                      select t1.*,
                             t2.tweet_id,
                             t2.postedtime,
                             t3.median_sentiment_index
                      from gptext.search(
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
          group by posted_date
    '''
    return sql.format(search_term=search_term)

def getAdjectivesCloud(search_term):
    '''
       Return a dict to generate a word cloud out of all adjectives associated with the search_term
    '''
    sql = '''
        with token_freq_query
                as
                (
            select token, count(*) as frequency
            from
            (
                select t1.*,
                       t2.tweet_id,
                       t2.postedtime,
                       t3.indx,
                       lower(t3.token) as token,
                       t3.tag
                from gptext.search(
                        TABLE(select * from topicdemo.tweet_dataset),
                        'vatsandb.topicdemo.tweet_dataset',
                        '{search_term}',
                        null
                     ) t1,
                     topicdemo.tweet_dataset t2,
                     sentimentdemo.training_data_pos_tagged t3
                     where t1.id = t2.id and t2.tweet_id = t3.id and t3.tag = 'A'
            ) q1
            group by token
        ) 
        select token, 
               (frequency*1.0/(select max(frequency) from token_freq_query))::float as normalized_frequency
        from token_freq_query
    '''
    return sql.format(search_term=search_term)


def getDayHourHeatMapSQL(search_term):
    '''
       Return rows of the form "day", "hour", "number of matching tweets"
    '''
    sql = '''
                select day_of_week,
                       hour_of_day,
                       count(tweet_id) as num_tweets,
                       avg(median_sentiment_index) as mean_sentiment_index,
                       count(tweet_id) FILTER (WHERE median_sentiment_index > 1) AS positive_count,
                       count(tweet_id) FILTER (WHERE median_sentiment_index < -1) AS negative_count,
                       count(tweet_id) FILTER (WHERE median_sentiment_index BETWEEN -1 AND 1) AS neutral_count
                from
                (
                       select t1.*,
                              t2.tweet_id,
                              t2.postedtime,
                              t3.median_sentiment_index,
                              extract(DOW from t2.postedtime) as day_of_week,
                              extract(HOUR from t2.postedtime) as hour_of_day
                       from gptext.search (
                              TABLE(select * from topicdemo.tweet_dataset),
                              'vatsandb.topicdemo.tweet_dataset',
                              '{search_term}',
                              null
                            ) t1,
                            topicdemo.tweet_dataset t2,
                            sentimentdemo.training_data_scored t3
                       where t1.id = t2.id and t2.tweet_id = t3.id and t3.median_sentiment_index IS NOT NULL
                )q
                group by day_of_week, hour_of_day
                order by day_of_week, hour_of_day
    '''
    return sql.format(search_term=search_term)

def sentimentNERTaggerSql(search_term):
    '''
        ========================= The following PL/Python functions should have already been run ==============================
        --1) Declare type to hold NER tagged results
        drop type if exists ner_tuple cascade;
        create type ner_tuple
        as
        (
            token text,
            ner_tag text
        );


        --2) Define PL/Python wrapper on NLTK's NER Tagger.
        create or replace function sentimentdemo.stanford_ner_tag(tweet text[])
            returns setof ner_tuple
        as
        $$
            import sys
            from nltk.tag.stanford import NERTagger
            if not sys.modules.has_key('stanford_ner_tagger'):
                sys.modules['stanford_ner_tagger'] = NERTagger('/usr/local/greenplum-db/lib/postgresql/java/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                      '/usr/local/greenplum-db/lib/postgresql/java/stanford-ner/stanford-ner.jar')
            ner_tagger = sys.modules['stanford_ner_tagger']  
                    
            tagged_result = ner_tagger.tag(tweet)
            return tagged_result
        $$language plpythonu;


        --3) Sample invocation
        select (t).token, 
              (t).ner_tag
        from
        (
            select sentimentdemo.stanford_ner_tag(ARRAY['Obama','is','the','president','of','USA']) as t
        ) q

        --4) Run it on the tweet dataset for sentiment demo.
        drop table if exists sentimentdemo.training_data_ner_tagged cascade;
        create table sentimentdemo.training_data_ner_tagged
        as
        (
                select id,
                        (ner).token,
                        (ner).ner_tag
                from
                (
                        select id,
                                sentimentdemo.stanford_ner_tag(tokens) as ner
                        from
                        (
                                select id, 
                                        array_agg(token) as tokens
                                from
                                (
                                        select id,
                                                token
                                        from sentimentdemo.training_data_pos_tagged
                                ) q1 group by id
                        ) q2
                ) q3
        ) distributed by (id);
        ===================================================================================================================================================================
    '''
    sql = '''
        with token_freq_query
        as
        (
            select token, 
                   ner_tag,
                   count(*) as frequency
            from
            (
                select  tweet_id,
                        (ner).token,
                        (ner).ner_tag
                from
                (
                    select tweet_id, 
                           sentimentdemo.stanford_ner_tag(array_agg(token order by indx)) as ner
                    from
                    (
                        select t1.*,
                               t2.tweet_id,
                               t2.postedtime,
                               t3.indx,
                               t3.token,
                               t3.tag
                        from gptext.search(
                                TABLE(select * from topicdemo.tweet_dataset),
                                'vatsandb.topicdemo.tweet_dataset',
                                '{search_term}',
                                null
                             ) t1,
                             topicdemo.tweet_dataset t2,
                             sentimentdemo.training_data_pos_tagged t3
                             where t1.id = t2.id and t2.tweet_id = t3.id
                     )q1
                ) q2
            ) q3
            group by token
        ) 
        select token, 
               (frequency*1.0/(select max(frequency) from token_freq_query))::float as normalized_frequency
        from token_freq_query
    '''
    return sql.format(search_term=search_term)
