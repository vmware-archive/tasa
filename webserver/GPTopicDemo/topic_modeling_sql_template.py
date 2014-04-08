# -*- coding: utf-8 -*-
'''
   Srivatsan Ramanujam<sramanujam@gopivotal.com>
   Collection of SQL templates to be used in building a topic dashboard
'''

#To speed things up and reduce response time, we'll restrict the number of documents to the run LDA on to the top {relevant_rows_limit} (by solr relevance score).
relevant_rows_limit = 1000

#For the force-directed topic graph, we'll show the top-200 most relevant nodes
relevant_nodes_limit_topic_graph=200

#Percentile threshold for edge pruning
pruning_threshold = 50

#Rank based pruning. Only consider top-k edges for each node, by edge-weight.
pruning_rank = 3

#The following code chunk should have been run before the functions in this module are invoked - to ensure that the table & indices exist
'''
        --i) Create Index using GPText
        select gptext.drop_index('topicdemo','tweet_dataset');

        --a) Create Empty Index
        select * from gptext.create_index('topicdemo','tweet_dataset','id','body');


        --b) Enable the Social Media Tokenizer for the tweet body field, before populating the index
            -- (i)   Run: gptext-config -f schema.xml -i vatsandb.topicdemo.tweet_dataset
            -- (ii)  Replace the field "text_intl" with "text_sm" against the entry : <field indexed="true" name="body" stored="false" termPositions="true" termVectors="true" type="text_sm"/>
            -- (iii) Exit the editor by saving the changes (:wq). This has enabled social media tokenizer for the tweet body

        --c) Enable terms table
        select gptext.enable_terms('vatsandb.topicdemo.tweet_dataset','body');           
        
        --d) Populate Index
        select * from gptext.index(TABLE(select * from topicdemo.tweet_dataset), 'vatsandb.topicdemo.tweet_dataset');

        --e) Commit Index
        select * from gptext.commit_index('vatsandb.topicdemo.tweet_dataset');

        --f) Enable Terms Table for the whole index (we will then only filter relevant documents matching a search term from this)
        drop table if exists topicdemo.tweet_dataset_terms_all cascade;
        create table topicdemo.tweet_dataset_terms_all 
        as
        (
            select *
            from gptext.terms(
                 TABLE(select * from topicdemo.tweet_dataset),
                 'vatsandb.topicdemo.tweet_dataset',
                 'body',
                 '*:*',
                 null
            )
            -- Disregard @mentions and http links
            -- Including it here as this is a costly operation if included for every search query
            where term !~* '^@' 
                  and term !~* '^http'  
                  and term != 'rt' 
                  and term != 'lt' 
                  and term != 'amp' 
                  and term != 'gt'
                  and term != 'tco'           
        ) distributed by (id);

       -- h) Some use UDF's in PL/Python which will be used throughout the demo
             --(1) KL-Divergence (Note this is not symmetric).

             -- See : http://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence
             -- D_KL(P||Q) = Sum_i(ln(P(i)/Q(i))P(i)).
             -- Ensure that P(i),Q(i) are never 0 (by applying smoothing).
                DROP FUNCTION IF EXISTS topicdemo.kl_div(float[], float[]);
                CREATE FUNCTION topicdemo.kl_div(p float[], q float[])
                RETURNS float 
                AS 
                $$
                     epsilon = 1e-20
                     base_dist = [ (p_x+epsilon)/(sum(p)+len(p)*epsilon) for p_x in p]
                     new_dist = [ (q_x+epsilon)/(sum(q)+len(q)*epsilon) for q_x in q]
                     from math import log
                     #Returns the KL-divergence of dist. Q from dist. P
                     return sum([log(base_dist[i]/new_dist[i])*base_dist[i] for i in range(len(base_dist))])
                $$ LANGUAGE PLPYTHONU;

                -- Entropy Measure
                DROP FUNCTION IF EXISTS topicdemo.information_entropy(float8[]) CASCADE;
                CREATE OR REPLACE FUNCTION topicdemo.information_entropy(prob_counts float8[])
                   RETURNS float8 
                AS
                $$
                     from math import log
                     #Smoothing
                     epsilon = 1e-20
                     probs = [(p+epsilon)/(sum(prob_counts)+epsilon*len(prob_counts)) for p in prob_counts]
                     entropy = sum([-1.0*p_i*log(p_i,2.0) for p_i in probs])
                     return entropy
                $$ LANGUAGE PLPYTHONU;


             --(2) Max & min element with index
                DROP TYPE IF EXISTS elem_index_pair CASCADE;
                CREATE TYPE elem_index_pair
                AS
                (
                    elem float,
                    index int
                );

                DROP FUNCTION IF EXISTS topicdemo.extreme_element_and_index(float[],boolean) CASCADE;
                CREATE OR REPLACE FUNCTION topicdemo.extreme_element_and_index(arr float[],is_minimum boolean)
                    RETURNS elem_index_pair
                AS
                $$
                      extreme_func = min if is_minimum else max
                      return [extreme_func(arr),arr.index(extreme_func(arr))]
                $$LANGUAGE PLPYTHONU;

             --(3) Unnest an array and return the elements with their ordinal positions
                DROP FUNCTION IF EXISTS topicdemo.unnest_with_ordinality(float8[]) CASCADE;
                CREATE OR REPLACE FUNCTION topicdemo.unnest_with_ordinality(arr float8[])
                    RETURNS SETOF elem_index_pair 
                AS
                $$
                    return [(arr[i],i) for i in range(len(arr))]
                $$ LANGUAGE PLPYTHONU;  
            
             --(4) Percentile 

                DROP FUNCTION IF EXISTS topicdemo.percentile_threshold(float[],float) cascade;
                CREATE OR REPLACE FUNCTION topicdemo.percentile_threshold(arr float[], percentile float)
                    RETURNS float
                AS
                $$
                    import numpy
                    return numpy.percentile(arr,percentile)
                $$language plpythonu; 
'''

def retrieveMatchingTweets(search_term,suffix_id):
    '''
       Create a table of matching tweets for the given search term.
    '''

    sql = '''
                -- 1) Create Terms Table
                
                drop table if exists topicdemo.terms_unfiltered_{suffix_id} cascade;
                create table topicdemo.terms_unfiltered_{suffix_id}
                as
                (
                     select terms.*,
                            relevant.score
                     from
                     (
                         select s.id, 
                                s.score
                         from gptext.search(
                                   TABLE(select * from topicdemo.tweet_dataset),
                                   'vatsandb.topicdemo.tweet_dataset',
                                   '{search_term}',
                                   null
                         ) s
                         order by score desc
                         limit {relevant_rows_limit}
                     ) relevant, topicdemo.tweet_dataset_terms_all terms
                     where relevant.id = terms.id
                ) distributed by (id);

                --2) Filter out terms which are common to every document
                --   If only I had a GPText function to get the stemmed form of a word!!        

                drop table if exists topicdemo.tweet_dataset_terms_{suffix_id} cascade;
                create table topicdemo.tweet_dataset_terms_{suffix_id}
                as
                (
                        select topicdemo.terms_unfiltered_{suffix_id}.*
                        from topicdemo.terms_unfiltered_{suffix_id}, 
                        (
                                select t1.*,
                                       t2.total_docs
                                from
                                (
                                        select term,
                                               count(id) as num_docs
                                        from topicdemo.terms_unfiltered_{suffix_id}
                                        group by term
                                ) t1,
                                (
                                        select count(*) as total_docs
                                        from
                                        (
                                                 select id
                                                 from topicdemo.terms_unfiltered_{suffix_id}
                                                 group by id
                                        ) q
                                ) t2
                                where num_docs < total_docs
                        ) filtered_terms
                        where topicdemo.terms_unfiltered_{suffix_id}.term = filtered_terms.term
                ) distributed by (id);

    '''

    return sql.format(search_term=search_term, suffix_id=suffix_id,relevant_rows_limit=relevant_rows_limit)

def countOfMatchingTweets(search_term, suffix_id):
    '''
       Return number of tweets which matched the input query.
    '''
    
    sql =  '''
            select gptext.search_count('vatsandb.topicdemo.tweet_dataset','{search_term}',null) as num_matching_tweets;
    '''

    return sql.format(search_term=search_term)

def prepareDatasetForLDA(search_term,suffix_id):
    '''
       From the extracted Terms table, prepare the datasets required to run the LDA model.
    '''
    sql = '''
                -- 2) Create Term Dictionary
        
                drop table if exists topicdemo.tweet_dataset_terms_lookup_{suffix_id} cascade;
                create table topicdemo.tweet_dataset_terms_lookup_{suffix_id} 
                as
                (
                        select row_number() over(order by term asc) as idx,
                               term, 
                               term_freq
                        from
                        (
                                select term,
                                       count(*) as term_freq
                                from topicdemo.tweet_dataset_terms_{suffix_id}
                                where term is not null
                                group by term
                        ) q
                        -- Could perform frequency filtering to minimize size of vocabulary (uncomment below line if you want to consider it) 
                        -- disregard terms which occur less than 2 times (eliminate long tail)
                        -- where term_freq > 2
                ) distributed by (idx); 

                -- 3) Convert text into integers, for bag-of-words model.
                --    Convert every tweet into an array of numbers, where the numbers correspond to the token index in the terms table

                drop table if exists topicdemo.twitter_wm_lda_temp_{suffix_id} cascade;
                create table topicdemo.twitter_wm_lda_temp_{suffix_id} 
                as 
                (
                        select id, array_agg(term_number order by pos_idx) as contents
                        from
                        (
                                select t1.id, 
                                       t1.term, 
                                       t2.idx as term_number, 
                                       unnest(positions) as pos_idx 
                                from topicdemo.tweet_dataset_terms_{suffix_id} t1, 
                                     topicdemo.tweet_dataset_terms_lookup_{suffix_id} t2
                                where t1.term = t2.term
                                order by id, pos_idx
                        ) q1 group by id
                ) distributed by (id);

                -- 4) Create dict for the LDA model

                drop table if exists topicdemo.tweet_dataset_terms_dict_{suffix_id} cascade;
                create table topicdemo.tweet_dataset_terms_dict_{suffix_id} 
                as 
                (
                        select array_agg( distinct term) as dict 
                        from topicdemo.tweet_dataset_terms_lookup_{suffix_id}
                );

    '''
    return sql.format(search_term=search_term,suffix_id=suffix_id)
    
def runLDAModel(suffix_id,num_topics):
    '''
        Run the topic model with num_topics
    '''
    sql = '''
                drop table if exists topicdemo.twitter_wm_lda_mdl_{num_topics}topics_{suffix_id} cascade;
                drop table if exists topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id} cascade;
                select madlib_v05.plda_run 
                (
                        'topicdemo.twitter_wm_lda_temp_{suffix_id}',
                        'topicdemo.tweet_dataset_terms_dict_{suffix_id}',
                        'topicdemo.twitter_wm_lda_mdl_{num_topics}topics_{suffix_id}',
                        'topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id}',
                        30, -- num iterations of the Gibbs sampler
                        {num_topics}, -- num topics
                        1.0/{num_topics}, -- alpha prior (topic distributions under a document)
                        0.1 -- beta prior (word distribution under topics)
                );
    '''
    return sql.format(suffix_id=suffix_id,num_topics=num_topics)

def exportTopicAssignments(suffix_id,num_topics):
    '''
       Export the results of the topic modeling to a csv file, so that it can be passed through a word cloud gen
    '''
    sql = '''
                drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_cloud_{suffix_id} cascade;
                create table topicdemo.twitter_wm_lda_{num_topics}topics_cloud_{suffix_id}
                as 
                (
                        select topic_num, 
                               array_upper(word_allocs,1) as word_count, 
                               word_allocs 
                        from
                        (
                                select topic_num, 
                                       array_agg(word) as word_allocs
                                from 
                                (
                                        select id, 
                                               topic_num, 
                                               word_int, 
                                               lookup.term as word 
                                        from 
                                        (
                                               select id, 
                                                      unnest((topics).topics) as topic_num, 
                                                      unnest(contents) as word_int        
                                               from topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id}
                                        ) q1, topicdemo.tweet_dataset_terms_lookup_{suffix_id} lookup 
                                        where q1.word_int = lookup.idx
                                ) q2
                                group by topic_num
                        ) q3
                ) distributed by (topic_num);

    '''
    return sql.format(suffix_id=suffix_id,num_topics=num_topics)

def generateTopicGraph(search_term,suffix_id,num_topics):
    '''
       Generate a topic graph. This involves four steps documented inline
    '''
    
    sql = '''
          --(i) Compute topic distributions for each tweet and label each tweet with the topic that has max probability in it

              drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_dist_{suffix_id} cascade;
              create table topicdemo.twitter_wm_lda_{num_topics}topics_dist_{suffix_id}
              as 
              (
                      with tweets_with_entropy
                      as
                      (
                             select id,
                                    body,
                                    topics as topics_dist_count, 
                                    madlib.array_scalar_mult(topics, 1.0/total_words) as topics_dist_prob,
                                    --The topic with max probability is labeled as the topic for this tweet
                                    (topicdemo.extreme_element_and_index(topics,FALSE)).index+1 as label,
                                    --Information Entropy of the topic distribution of the tweet
                                    --High entropy implies the topics have more or less uniform distribution, we are interested in tweets with low entropy
                                    topicdemo.information_entropy(topics) as entropy,
                                    --Relevance score of the tweet_dataset
                                    score
                             from 
                             (
                                    select t1.id,
                                           t1.topics,
                                           t1.total_words,
                                           t2.score,
                                           t3.body
                                    from
                                    (
                                            select id, 
                                                  (topics).topic_d::float8[] as topics,
                                                  madlib.array_sum((topics).topic_d)::float8 as total_words
                                           from topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id}
                                    ) t1, 
                                    (
                                           select id,
                                                  score
                                           from gptext.search(
                                                     TABLE(select * from topicdemo.tweet_dataset),
                                                    'vatsandb.topicdemo.tweet_dataset',
                                                    '{search_term}',
                                                    null
                                           )
                                    ) t2,
                                    topicdemo.tweet_dataset t3
                                    where t1.id = t2.id and t2.id = t3.id                           
                             ) topic_dist_stats
                  ),
                  topk_percentile
                  as
                  (
                       select topicdemo.percentile_threshold(array_agg(entropy), 25) as threshold
                       from  tweets_with_entropy
                  ) 
                  select *
                  from tweets_with_entropy, topk_percentile
                  --where entropy < threshold
                  -- To make the graph look interesting we are introducing a bit of randomness here, so long as the given node fell into the top-50% in terms of entropy
                  --order by entropy
                  -- Select top-k relevant tweets, whose entropy is less than the specified threshold
                  order by score desc
                  limit {relevant_nodes_limit_topic_graph}
              ) distributed by (id);

          --(ii) Compute the node centroids to compute inter-cluster strength

              drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}_centroids cascade;
              create table topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}_centroids
              as
              (
                  select label,
                  -- Normalize the array to make them as probabilities
                  madlib_v05.array_scalar_mult(mean_topic_prob_arr, (1.0/madlib_v05.array_sum(mean_topic_prob_arr))) as topic_prob_centroid
                  from
                  (
                       select label,
                              array_agg(mean_topic_prob order by topic) as mean_topic_prob_arr
                       from
                       (
                              select label,
                                     topic,
                                     avg(topic_prob) as mean_topic_prob
                              from
                              (
                                     select id, 
                                            label,
                                            (pair).index as topic,
                                            (pair).elem as topic_prob
                                     from
                                     (
                                            select nodes.id, 
                                                   nodes.label, 
                                                   topicdemo.unnest_with_ordinality(nodes.topics_dist_prob) as pair
                                            from topicdemo.twitter_wm_lda_{num_topics}topics_dist_{suffix_id} nodes
                                     ) q1
                              ) q2
                              group by label, topic
                       ) q3
                       group by label
                  ) q4
              ) distributed by (label);
  
          --(iii) Add the centroids and the nodes into a single table of nodes & edges

              drop table if exists topicdemo.twitter_wm_lda_{num_topics}_nodes_with_centroids_{suffix_id} cascade;
              create table topicdemo.twitter_wm_lda_{num_topics}_nodes_with_centroids_{suffix_id}
              as
              (
                   select id::text,
                          body,
                          label,
                          topics_dist_prob
                   from topicdemo.twitter_wm_lda_{num_topics}topics_dist_{suffix_id}
                   --Add the centroids as well
                   union all
                   --
                   select 'topic_centroid_'||label as id,
                          'topic_centroid_'||label as body,
                          label,
                          topic_prob_centroid as topics_dist_prob
                   from topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}_centroids
              ) distributed by (id);
             
          --(iv) Compute the KL-divergence of tweets within a topic and use this as edge weights. 
          --     This will be of the form [tweet_i, tweet_i_body, tweet_j, tweet_j_body, label, edge_weight]
              
              drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id} cascade;
              create table topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}
              as
              (
                  with topic_graph
                  as
                  (
                      select t1.id as tweet_i,
                             t1.body as tweet_i_body,
                             t2.id as tweet_j,
                             t2.body as tweet_j_body,
                             t1.label as label,
                             -- divergence = KL_Div(P||Q)+KL_Div(Q||P)
                             (
                                   topicdemo.kl_div(t1.topics_dist_prob,t2.topics_dist_prob)+ 
                                   topicdemo.kl_div(t2.topics_dist_prob,t1.topics_dist_prob)
                             ) as divergence
                      from topicdemo.twitter_wm_lda_{num_topics}_nodes_with_centroids_{suffix_id} t1,
                           topicdemo.twitter_wm_lda_{num_topics}_nodes_with_centroids_{suffix_id} t2
                      -- Only compute intra-topic edge weights and inter-centroid edge weights
                      where ((t1.label = t2.label) OR (t1.id ~* 'topic_centroid_' and t2.id ~* 'topic_centroid_')) and t1.id < t2.id 
                  )
                  -- divergence is a measure of dissimilarity, we will then transform it into a measure of similarity
                  select tgraph.*,
                         (max_div.max_divergence - tgraph.divergence) as edge_weight
                  from topic_graph tgraph,
                       (
                           select max(divergence) as max_divergence
                           from topic_graph
                       ) max_div
              ) distributed by (tweet_i);
    '''
    return sql.format(search_term=search_term,suffix_id=suffix_id, num_topics=num_topics, relevant_nodes_limit_topic_graph=relevant_nodes_limit_topic_graph)

def getTopicGraphQuery(suffix_id, num_topics, prune='none'):
    ''' 
       Return query to fetch the topic graph.
    '''
    sql = ''
    if(prune == 'none'):
        sql = '''
              select tweet_i,
                     tweet_i_body,
                     tweet_j,
                     tweet_j_body,
                     label,
                     edge_weight
              from topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}          
        '''.format(suffix_id=suffix_id, num_topics=num_topics)
    elif(prune=='percentile'):
        sql = '''
              select t1.tweet_i,
                     t1.tweet_i_body,
                     t1.tweet_j,
                     t1.tweet_j_body,
                     t1.label,
                     t1.edge_weight
              from topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id} t1,
                   (
                         select label,
                                topicdemo.percentile_threshold(array_agg(edge_weight),{pruning_threshold}) as threshold_top_n_percentile
                         from topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}
                         group by label
                   ) t2
              where t1.label = t2.label and
                    t1.edge_weight > t2.threshold_top_n_percentile
        '''.format(suffix_id=suffix_id, num_topics=num_topics, pruning_threshold=pruning_threshold)
    else:
        #Pruning by rank
        sql = '''
                 select *
                 from
                 (
                     select t1.*,
                     rank() over(partition by tweet_i order by edge_weight desc)
                     from topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id} t1
                 )q 
                 where rank<= {pruning_rank}
        '''.format(suffix_id=suffix_id, num_topics=num_topics, pruning_rank=pruning_rank)

    return sql

def getNumTweetsPerTopic(suffix_id, num_topics):
    '''
       Return number of tweets by per topic
    '''
    sql = '''
             select label,
                    count(id) as num_tweets
             from
             (
                    select id, 
                           (topics).topic_d::float8[] as topics,
                           (topicdemo.extreme_element_and_index((topics).topic_d::float8[],FALSE)).index+1 as label
                    from topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id}
             ) q
             group by label
    '''
    return sql.format(suffix_id=suffix_id, num_topics=num_topics)


def getTopicResults(suffix_id, num_topics):
    '''
       Return the topic allocation results of the form || topic_num | word_count | word_allocs || 
    '''
    sql = '''select topic_num, word_count, word_allocs from  topicdemo.twitter_wm_lda_{num_topics}topics_cloud_{suffix_id};'''
    return sql.format(suffix_id=suffix_id, num_topics=num_topics) 


def getCleanUpQuery(suffix_id,num_topics):
     '''
        Clean-up all the tables that were generated
     '''
     sql = '''
           drop table if exists topicdemo.terms_unfiltered_{suffix_id} cascade;
           drop table if exists topicdemo.tweet_dataset_terms_{suffix_id} cascade;
           drop table if exists topicdemo.tweet_dataset_terms_lookup_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_temp_{suffix_id} cascade;
           drop table if exists topicdemo.tweet_dataset_terms_dict_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_mdl_{num_topics}topics_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_mdl_{num_topics}topics_result_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_cloud_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_dist_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id} cascade;
           drop table if exists topicdemo.twitter_wm_lda_{num_topics}topics_graph_{suffix_id}_centroids;
           drop table if exists topicdemo.twitter_wm_lda_{num_topics}_nodes_with_centroids_{suffix_id};
     '''
     return sql.format(suffix_id=suffix_id,num_topics=num_topics)
