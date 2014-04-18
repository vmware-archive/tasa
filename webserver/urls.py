# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url   
import settings
import os
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #Mapping for new UI code
    url(r'^tasa/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT + 'tasa/'}),
    #Mapping for the TASA Queries
    url(r'^gp/tasa/relevant_tweets/','webserver.TASADemo.views.relevant_tweets', name='relevant_tweets'),
    url(r'^gp/tasa/relevant_tweets_for_day/','webserver.TASADemo.views.relevant_tweets_for_day', name='relevant_tweets_for_day'),
    url(r'^gp/tasa/relevant_tweets_for_day_and_sentiment/','webserver.TASADemo.views.relevant_tweets_for_day_and_sentiment', name='relevant_tweets_for_day_and_sentiment'),

    #Mapping for media files - images/icons etc
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^stat/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),    
    #Mapping for time series plots    
    url(r'^gp/topic/ts/','webserver.GPTopicDemo.views.tweets_over_time',name='tweetsovertime'),
    #Mapping for Topic Engine
    url(r'^gp/topic/home','webserver.GPTopicDemo.views.topic_home', name='topichome'),
    url(r'^gp/topic/fetch/','webserver.GPTopicDemo.views.topic_fetch', name='topicfetch'),
    #Standalone word cloud generator for LDA results
    url(r'^gp/topic/tcloudgen/gen/','webserver.GPSentiDemo.views.generate_topic_cloud_from_form',name='generatetopiccloudfromform'),
    url(r'^gp/topic/tcloudgen/home','webserver.GPSentiDemo.views.topic_cloud_home',name='topiccloudhome'),
    #Mapping for the Sentiment Analysis Engine
    url(r'^gp/senti/home','webserver.GPSentiDemo.views.senti_home', name='sentihome'),
    url(r'^gp/senti/fetch/','webserver.GPSentiDemo.views.senti_fetch', name='sentifetch'),
    url(r'^gp/senti/ms/','webserver.GPSentiDemo.views.multi_series_sentiment_plot',name='multiseriessentimentplot'),    
    url(r'^gp/senti/acloud/','webserver.GPSentiDemo.views.generate_adjectives_cloud',name='generateadjectivescloud'),
    url(r'^gp/senti/hmap/','webserver.GPSentiDemo.views.dayhour_hmap',name='dayhourhmap'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    #Mapping for new UI code
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT + 'tasa/'}),
)
