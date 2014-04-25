'''
Srivatsan Ramanujam<sramanujam@gopivotal.com>
Collection of SQL templates for time series related plots on the tweets dataset
'''

def numTweetsByDate(search_term, suffix_id):
    '''
        Return the number of tweets matching the search term for each date
    '''
    sql = '''
          select posted_date,
                 count(id) as num_tweets
          from
          (
              select match.id,
                     (master.postedtime at time zone 'UTC')::date as posted_date
              from
              (
                  select id, 
                         score
                  from gptext.search(
                           TABLE(select * from topicdemo.tweet_dataset),
                           'vatsandb.topicdemo.tweet_dataset',
                           '{search_term}',
                           null
                       )
              ) match, topicdemo.tweet_dataset master
              where match.id = master.id
          )q
          group by posted_date
    '''
    return sql.format(search_term=search_term)