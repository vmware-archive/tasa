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
    sideBarTweets = new Backbone.Collection(),
    sideBar = new (Backbone.Model.extend({
       url: function() { return '/gp/tasa/relevant_tweets/?sr_trm='  + query.get('query'); },
       parse: function(attrs) {
         this.set('totalTweets', attrs.count);
         _.each(attrs.tweets, function(tweet) {
           _.forIn(tweet, function(value, key) {
             tweet[key] = _.unescape(eval('"' + value.replace(/"/g, '\\x22').replace(/\r\n|\n/gm, '\\x0A') + '"'));
           });
         });
         sideBarTweets.reset(attrs.tweets);
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
    adjectives = new (Backbone.Collection.extend({
       url: function() { return '/gp/senti/acloud/q?sr_trm=' + query.get('query'); },
       parse: function(response) { return response.adjective_cloud; },
       comparator: 'normalized_frequency'
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
      return {tweets: sideBarTweets.toJSON(), totalTweets: sideBar.get('totalTweets')};
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
    _.invoke([totalTweets, sideBar, sentiment, heatmap, adjectives], 'fetch', {reset: true});
  });
})();