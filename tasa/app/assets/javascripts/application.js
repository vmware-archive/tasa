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
      url: function() { return '/gp/tasa/total_tweets/q?sr_trm=' + query.get('query'); },
      comparator: 'posted_date',
      model: Backbone.Model.extend({
        idAttribute: 'posted_date',
        parse: function(data) { return _.extend(data, {posted_date: new Date(data.posted_date)}); }
      }),
      toJSON: function() {
        return [
          {
            name: 'Tweets',
            className: 'total',
            color: 'rgba(234, 239, 235, .8)',
            data: this.map(function(model, i) { return {x: i, y: model.get('counts').total, posted_date: model.get('posted_date')}; })
          }
        ];
      }
    }))(),
    sideBar = new (Backbone.Model.extend({
       url: function() {
         return '/gp/tasa/top_tweets/q?' + $.param({
           sr_trm: query.get('query'),
           sr_adj: this.get('adjective'),
         });
       },
       parse: function(attrs) {
         _.each(attrs.tweets, function(tweets, type) {
           _.each(tweets, function(tweet) {
             _.forIn(tweet, function(value, key) {
               if (!_.isString(value)) { return; }
               tweet[key] = _.unescape(eval('"' + value.replace(/"/g, '\\x22').replace(/\r\n|\n/gm, '\\x0A').replace(/\\/, '\\x5c') + '"'));
             });
           });
         });
         return attrs;
       }
     }))(),
    sentimentMapping = new (Backbone.Collection.extend({
      url: function() { return '/gp/tasa/sentiment_mapping/q?sr_trm=' + query.get('query'); },
      comparator: 'posted_date',
      model: Backbone.Model.extend({
        idAttribute: 'posted_date',
        parse: function(data) { return _.extend(data, {posted_date: new Date(data.posted_date)}); }
      }),
      toJSON: function() {
        return [
          {
            name: 'Positive tweets',
            className: 'positive',
            color: '#80a55d',
            data: this.map(function(model, i) { return {x: i, y: model.get('counts').positive, posted_date: model.get('posted_date')}; })
          },
          {
            name: 'Negative tweets',
            className: 'negative',
            color: '#ce522c',
            data: this.map(function(model, i) { return {x: i, y: model.get('counts').negative, posted_date: model.get('posted_date')}; })
          },
          {
            name: 'Neutral tweets',
            className: 'neutral',
            color: 'rgba(234, 239, 235, .3)',
            data: this.map(function(model, i) { return {x: i, y: model.get('counts').neutral, posted_date: model.get('posted_date')}; })
          }
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
      url: function() { return '/gp/tasa/adjectives/q?sr_trm=' + query.get('query'); },
      comparator: 'normalized_frequency',
      model: Backbone.Model.extend({
        idAttribute: 'word'
      })
     }))(),
    tweetActivity = new (Backbone.Collection.extend({
      url: function() { return '/gp/tasa/tweet_activity/q?sr_trm=' + query.get('query'); },
      model: Backbone.Model.extend({
        idAttribute: 'timestamp',
        parse: function(data) { return _.extend(data, {timestamp: Number(new Date(2013, 5, 31)) + data.day * 1000 * 60 * 60 * 24 + data.hour * 1000 * 60 * 60 }); }
      }),
      toJSON: function() {
        return this.reduce(function(result, model) {
          result[model.get('timestamp') / 1000] = model.get('counts').total;
          return result;
        }, {});
      }
    }))()
   ;

  $('body').html(JST['templates/application']);

  var sidebarView = new SpinnerView({
    el: $('.drilldown-content'),
    template: 'templates/sidebar_tweets',
    model: sideBar,
    decorator: function(options) {
      if (options.loading) { return {}; }

      return _.extend(this.model.omit('tweets'), {
        date: sideBar.has('posted_date') && d3.time.format.utc('%B %d, %Y')(new Date(sideBar.get('posted_date'))) ||
              sideBar.has('heatmap') && d3.time.format('%As at %I%p')(new Date(sideBar.get('heatmap'))).replace(/at 0/, 'at ') ||
              'July 1 - 31, 2013',
        title: this.model.get('sentiment') && 'Sentiment Mapping' ||
               this.model.get('topic') && 'Topic Words' ||
               this.model.get('adjective') && 'Adjectives' ||
               this.model.get('heatmap') && 'Tweet Activity' ||
               'Top ' + this.model.get('tweets').total.length + ' Tweets',
        proportions: this.model.get('sentiment') && {
          positive_proportion: 100 * this.model.get('counts').positive / this.model.get('counts').total,
          negative_proportion: 100 * this.model.get('counts').negative / this.model.get('counts').total,
          neutral_proportion: 100 * this.model.get('counts').neutral / this.model.get('counts').total
        } || undefined,
        groups: _.map(this.model.get('tweets'), function(tweets, sentiment) {
          if (this.model.get('sentiment') && this.model.get('sentiment') !== sentiment) { return; }

          return {
            sentiment: sentiment,
            tweets: tweets,
            subtitle: (this.model.get('sentiment') || this.model.get('heatmap')) && 'Top ' + tweets.length + ' ' + sentiment + ' tweets' ||
                      this.model.get('adjective') && 'Top ' + tweets.length + ' tweets for "' + this.model.get('adjective') + '"' ||
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
    model: sentimentMapping
  });
  var heatmapView = new HeatmapView({
    el: $('.tweet-activity .heatmap-content'),
    model: tweetActivity
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
      xhrRequests = _.invoke([totalTweets, sideBar, sentimentMapping, tweetActivity, adjectives], 'fetch', {reset: true});
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

  function dirtyForm(e) {
    _.defer(function() {
      var $inputs = $(e.currentTarget).find('input');
      $inputs.each(function() {
        var $input = $(this);
        $input.toggleClass('changed', ($input.attr('value') || '') !== ($input.val() || ''));
      });
    });
  }
  $('body')
    .on('input', 'form', dirtyForm)
    .on('reset', 'form', dirtyForm)
  ;

  var sidebarXhrRequest;
  sideBar.on('change', function(sideBar, options) {
    if (sideBar.get('adjective') && sideBar.get('topic')) {
      var ids = _.result(force.get('topic_words')[sideBar.get('adjective')], sideBar.get('topic')) || [];
      sideBar.set(sideBar.parse({
        tweets: {total: _.values(_.pick(force.get('tweets'), ids))},
        counts: {total: ids.length}
      }), {silent: true});
      sideBar.trigger('sync');
    } else if (sideBar.get('heatmap')) {
      sideBar.set(sideBar.parse(tweetActivity.get(sideBar.get('heatmap')).toJSON()), {silent: true});
      sideBar.trigger('sync');
    } else if (sideBar.get('sentiment')) {
      sideBar.set(sideBar.parse(sentimentMapping.get(new Date(sideBar.get('posted_date'))).toJSON()), {silent: true});
      sideBar.trigger('sync');
    } else if (sideBar.get('posted_date')) {
      sideBar.set(sideBar.parse(totalTweets.get(new Date(sideBar.get('posted_date'))).toJSON()), {silent: true});
      sideBar.trigger('sync');
    } else {
      _.result(sidebarXhrRequest, 'abort');
      sidebarXhrRequest = sideBar.fetch();
    }
  });
})();