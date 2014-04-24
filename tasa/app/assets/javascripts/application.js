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

  var
    query = new Backbone.Model({query: ''}),
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
          {name: 'Tweets', data: this.map(function(model, i) { return _.extend(model.toJSON(), {x: i}); }), color: '#fff'}
        ];
      }
    }))(),
    sideBar = new (Backbone.Model.extend({
       url: function() {
         return '/gp/tasa/relevant_tweets/?' + $.param({
           sr_trm: query.get('query'),
           ts: this.get('posted_date'),
           snt: this.get('sentiment')
         });
       },
       parse: function(attrs) {
         _.each(attrs.tweets, function(tweet) {
           _.forIn(tweet, function(value, key) {
             tweet[key] = _.unescape(eval('"' + value.replace(/"/g, '\\x22').replace(/\r\n|\n/gm, '\\x0A') + '"'));
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
          {name: 'Positive tweets', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('positive_count')}}), color: '#d9e021'},
          {name: 'Negative tweets', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('negative_count')}}), color: '#e74d00'},
          {name: 'Neutral tweets', data: this.map(function(model, i){ return {posted_date: model.get('posted_date'), x: i, y: model.get('neutral_count')}}), color: 'rgba(255, 255, 255, 0.3)'}
        ];
      }
    }))(),
    force = new (Backbone.Model.extend({
      url: function() { return '/gp/topic/fetch/q?num_topics=3&sr_trm=' + query.get('query'); },
      parse: function(response) {
        var cloud = _.flatten(_.map(response.topic_cloud_d3, function(data, topic) {
          data = _.last(_.sortBy(data.word_freq_list, 'normalized_frequency'), 5);
          _.each(data, function(word) { word.topic = topic; });
          return data;
        }));
        return _.extend(JSON.parse(response.topic_graph), {cloud: cloud});
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
        return _.invoke(this.last(100), 'toJSON');
      }
     }))(),
    heatmap = new (Backbone.Collection.extend({
      url: function() { return '/gp/senti/hmap/q?sr_trm=' + query.get('query'); },
      parse: function(response) { return response.hmap; },
      toJSON: function() {
        return this.reduce(function(result, model) {
          result[new Date(2013, 5, 31) / 1000 + model.get('day') * 60 * 60 * 24 + model.get('hour') * 60 * 60] = model.get('num_tweets');
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
    decorator: function() {
      return _.extend(this.model.toJSON(), {
        date: sideBar.has('posted_date') ? d3.time.format.utc('%B %d, %Y')(new Date(sideBar.get('posted_date'))) : 'June 30 - July 31, 2013'
      });
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

  $('body').on('submit', '.query', function(e) {
    _.each($(e.currentTarget).serializeArray(), function(input) {
      query.set(input.name, input.value);
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

  query.on('change:query', function(query, value) {
    $('body').toggleClass('has-query', Boolean(value));
    _.invoke([totalTweets, sideBar, sentiment, heatmap, adjectives, force], 'fetch', {reset: true});
  });

  $('body').on('click', '.t1,.t2,.t3', function(e) {
    $('.topic-cluster')[0].dataset.selected = _.find(e.target.classList, function(className) { return className.match(/^t\d+$/); });
    e.stopPropagation();
  });

  $('body').on('click', '.topic-cluster', function() {
    delete $('.topic-cluster')[0].dataset.selected;
  });

  $('body').on('click', '.detail', function(e) {
    sideBar.set({
      posted_date: $(e.currentTarget).find('[data-posted-date]').data('posted-date'),
      sentiment: $(e.currentTarget).find('[data-sentiment]').data('sentiment')
    });
  });

  sideBar.on('change', function(sideBar, options) {
    if (options.xhr) { return; }
    sideBar.fetch();
  });
})();