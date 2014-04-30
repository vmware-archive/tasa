//= require jquery
//= require jquery_ujs
//= require lodash
//= require handlebars.runtime
//= require backbone
//= require rickshaw_with_d3
//= require cal-heatmap
//= require d3.layout.cloud
//= require_tree ./templates
//= require views/spinner
//= require views/time_series
//= require views/heatmap
//= require views/tag_cloud
//= require views/force
//= require bootstrap/tooltip
(function() {
  'use strict';

  var DEFAULT_TOPICS = 3;

  var
    query = new Backbone.Model({query: '', topics: 0}),
    totalTweets = new (Backbone.Collection.extend({
      model: Backbone.Model.extend({
        parse: function(response) { return {posted_date: new Date(response.posted_date), num_tweets: response.num_tweets} },
        toJSON: function() { return {posted_date: this.get('posted_date'), y: this.get('num_tweets')}; }
      }),
      comparator: 'posted_date',
      url: function() { return '/gp/topic/ts/q?sr_trm=' + query.get('query'); },
      parse: function(response) { return response.tseries; },
      toJSON: function() {
        return [
          {name: 'Tweets', className: 'total', data: this.map(function(model, i) { return _.extend(model.toJSON(), {x: i}); }), color: 'rgba(234, 239, 235, .8)'}
        ];
      }
    }))(),
    sideBar = new (Backbone.Model.extend({
       url: function() {
         return '/gp/tasa/relevant_tweets/?' + $.param({
           sr_trm: query.get('query'),
           sr_adj: this.get('adjective'),
           ts: this.get('posted_date'),
           snt: this.get('sentiment')
         });
       },
       parse: function(attrs) {
         if (_.isArray(attrs.tweets)) {
           var groups = {};
           groups[this.get('sentiment') || 'total'] = attrs.tweets;
           attrs.tweets = groups
         }
         _.each(attrs.tweets, function(tweets, type) {
           _.each(tweets, function(tweet) {
             _.forIn(tweet, function(value, key) {
               if (!_.isString(value)) { return; }
               tweet[key] = _.unescape(eval('"' + value.replace(/"/g, '\\x22').replace(/\r\n|\n/gm, '\\x0A').replace(/\\/, '\\x5c') + '"'));
             });
           });
         });
         return _.extend({tweets: attrs.tweets}, attrs.counts, {
           positive_proportion: 100 * attrs.counts.positive / attrs.counts.total,
           negative_proportion: 100 * attrs.counts.negative / attrs.counts.total,
           neutral_proportion: 100 * attrs.counts.neutral / attrs.counts.total
         });
       }
     }))(),
    sentiment = new (Backbone.Collection.extend({
      model: Backbone.Model.extend({
        parse: function(response) {
          return {
            posted_date: new Date(response.posted_date),
            negative_count: response.negative_count,
            positive_count: response.positive_count,
            neutral_count: response.neutral_count
          }
        }
      }),
      comparator: 'posted_date',
      url: function() { return '/gp/senti/ms/q?sr_trm=' + query.get('query'); },
      parse: function(response) { return response.multi_series; },
      toJSON: function() {
        return [
          {name: 'Positive tweets', className: 'positive', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('positive_count')}}), color: '#80a55d'},
          {name: 'Negative tweets', className: 'negative', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('negative_count')}}), color: '#ce522c'},
          {name: 'Neutral tweets', className: 'neutral', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('neutral_count')}}), color: 'rgba(234, 239, 235, .3)'}
        ];
      }
    }))(),
    force = new (Backbone.Model.extend({
      url: function() { return '/gp/topic/fetch/q?num_topics=' + query.get('topics') + '&sr_trm=' + query.get('query'); },
      parse: function(response) {
        var cloud = _.flatten(_.map(response.topic_cloud_d3, function(data, topic) {
          data = _.chain(data.word_freq_list).reject({word: 't.co'}).sortBy('normalized_frequency').last(10).value();
          _.each(data, function(word) { word.topic = topic; });
          return data;
        }));
        return _.extend(JSON.parse(response.topic_graph), {
          cloud: cloud,
          tweets: response.tweetid_to_body_dict,
          topic_words: response.topic_drilldown_dict});
      },
      toJSON: function() {
        return this.get('cloud');
      }
    }))(),
    adjectives = new (Backbone.Collection.extend({
      url: function() { return '/gp/senti/acloud/q?sr_trm=' + query.get('query'); },
      parse: function(response) { return response.adjective_cloud; },
      comparator: 'normalized_frequency',
      toJSON: function() {
        return _.invoke(this.last(64), 'toJSON');
      }
     }))(),
    heatmap = new (Backbone.Model.extend({
      url: function() { return '/gp/tasa/tweets/q?hmap=true&sr_trm=' + query.get('query'); },
      toJSON: function() {
        var self = this, result = {};
        self._timestampMap = {};
        _.each(this.get('tweet_ids_by_date'), function(row) {
          var timestamp = new Date(2013, 5, 31) / 1000 + row.day * 60 * 60 * 24 + row.hour * 60 * 60;
          result[timestamp] = row.counts.total;
          self._timestampMap[timestamp] = row;
        });
        return result;
      },
      data: function(timestamp) {
        return this._timestampMap[timestamp/1000];
      }
    }))()
   ;

  $('body').html(JST['templates/application']);

  var sidebarView = new SpinnerView({
    el: $('.drilldown-content'),
    template: 'templates/sidebar_tweets',
    model: sideBar,
    decorator: function() {
      return _.extend(this.model.omit('tweets'), {
        date: sideBar.has('posted_date') && d3.time.format.utc('%B %d, %Y')(new Date(sideBar.get('posted_date'))) ||
              sideBar.has('heatmap') && d3.time.format('%As at %I%p')(new Date(sideBar.get('heatmap'))).replace(/at 0/, 'at ') ||
              'July 1 - 31, 2013',
        title: this.model.get('sentiment') && 'Sentiment Mapping' ||
               this.model.get('topic') && 'Topic Words' ||
               this.model.get('adjective') && 'Adjectives' ||
               this.model.get('heatmap') && 'Tweet Activity' ||
               'Top 20 Tweets',
        groups: _.map(this.model.get('tweets'), function(tweets, sentiment) {
          return {
            sentiment: sentiment,
            tweets: tweets,
            subtitle: this.model.get('sentiment') && 'Top 20 ' + sentiment + ' tweets' ||
                      this.model.get('adjective') && 'Top 20 tweets for "' + this.model.get('adjective') + '"' ||
                      this.model.get('heatmap') && 'Top 10 ' + sentiment + ' tweets' ||
                      ''
          }
        }, this)
      });
    },
    render: function() {
      SpinnerView.prototype.render.apply(this, arguments);
      this.$el.parent().scrollTop(0);
    }
  });
  var totalTweetsView = new TimeSeriesView({
    el: $('.total-tweets .graph-content'),
    model: totalTweets
  });
  var sentimentView = new TimeSeriesView({
    el: $('.sentiment .graph-content'),
    model: sentiment
  });
  var heatmapView = new HeatmapView({
    el: $('.tweet-activity .heatmap-content'),
    model: heatmap
  });
  var adjectivesView = new TagCloudView({
    el: $('.adjectives .tag-cloud'),
    model: adjectives
  });
  var forceView = new ForceView({
    el: $('.topic-cluster .force'),
    model: force
  });
  var topicCloudView = new TagCloudView({
    el: $('.topic-cluster .tag-cloud'),
    model: force
  });

  $('body').on('submit', 'form', function(e) {
    var $form = $(e.currentTarget);

    _.each($form.serializeArray(), function(input) {
      if (input.name === 'query') {
        var parsedQuery = input.value.split(/\s*\|\s*/);
        query.set({query: parsedQuery[0], topics: parsedQuery[1] || DEFAULT_TOPICS});
      } else if (input.name === 'topics') {
        query.set(input.name, Number(input.value))
      }

      $form.find('[name="' + input.name + '"]').val(query.get(input.name));
    });
    $(document.activeElement).blur();
  });

  $('body').one('webkitTransitionEnd', function() {
    var
      queryNode =  $('.query'),
      queryThreshold = queryNode.offset().top,
      drilldownThreshold = $('.drilldown').offset().top,
      contentTop = $('.graphs').offset().top,
      start = queryThreshold + 130,
      finish = contentTop - queryNode.outerHeight() + 30
    ;
    $(window).scroll(function() {
      var scrollTop = $('body').scrollTop(),
          opacity = Math.min(Math.max((scrollTop - start) / (finish - start), 0), 0.99)
      ;
      queryNode.toggleClass('sticky',  scrollTop > queryThreshold);
      $('.drilldown').toggleClass('sticky',  scrollTop > drilldownThreshold);
      queryNode.css('background-color', queryNode.css('background-color').replace(/[\d.]+(?=\))/, opacity));
    });
  });

  var xhrRequests, forceXhrRequest;
  query.on('change', function(query) {
    var oldXhrRequests = xhrRequests;
    xhrRequests = [];

    sideBar.clear({silent: true});

    if (_.has(query.changedAttributes(), 'query')) {
      _.invoke(oldXhrRequests, 'abort');
      _.result(forceXhrRequest, 'abort');
      _.result(sidebarXhrRequest, 'abort');

      $('body').toggleClass('has-query', Boolean(query.get('query')));
      xhrRequests = _.invoke([totalTweets, sideBar, sentiment, heatmap, adjectives], 'fetch', {reset: true});
      forceXhrRequest = force.fetch({reset: true});
    } else if (_.has(query.changedAttributes(), 'topics')) {
      _.result(forceXhrRequest, 'abort');
      forceXhrRequest = force.fetch({reset: true});
    }
  });

  $('body').on('click', '[data-topic]', function(e) {
    $('.topic-cluster')[0].dataset.selected = $(e.currentTarget).data('topic');
    e.stopPropagation();
  });

  $('body').on('click', '.topic-cluster', function() {
    delete $('.topic-cluster')[0].dataset.selected;
  });

  $('body').on('click', '.detail, .tag-cloud text, .graph-rect', function(e) {
    sideBar.set({
      posted_date: $(e.currentTarget).find('[data-posted-date]').data('posted-date'),
      sentiment: $(e.currentTarget).find('[data-sentiment]').data('sentiment'),
      adjective: $(e.currentTarget).data('adjective'),
      topic: $(e.currentTarget).data('topic'),
      heatmap: $(e.currentTarget).data('heatmap-timestamp')
    });
  });

  var sidebarXhrRequest;
  sideBar.on('change', function(sideBar, options) {
    if (options.xhr) { return; }

    if (sideBar.get('adjective') && sideBar.get('topic')) {
      var ids = _.result(force.get('topic_words')[sideBar.get('adjective')], sideBar.get('topic')) || [];
      sideBar.set(sideBar.parse({
        tweets: _.values(_.pick(force.get('tweets'), ids)),
        counts: {total: ids.length}
      }), {silent: true});
      sideBar.trigger('sync');
    } else if (sideBar.get('heatmap')) {
      var data = heatmap.data(sideBar.get('heatmap'));
      _.each(data.tweets, function(ids, sentiment) {
        data.tweets[sentiment] = _.values(_.pick(heatmap.get('tweets_by_id'), ids));
      });
      sideBar.set(sideBar.parse(data), {silent: true});
      sideBar.trigger('sync');
    } else {
      _.result(sidebarXhrRequest, 'abort');
      sidebarXhrRequest = sideBar.fetch();
    }
  });
})();