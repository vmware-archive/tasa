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
//= require_tree ./views
//= require_tree ./behaviors
//= require bootstrap/tooltip
(function() {
  'use strict';

  var DEFAULT_TOPICS = 3;

  var TimeSeries = Backbone.Collection.extend({
    comparator: 'posted_date',
    model: Backbone.Model.extend({
      idAttribute: 'posted_date',
      parse: function(data) { return _.extend(data, {posted_date: new Date(data.posted_date)}); }
    })
  });

  function parseTweets(json) {
    _.each(json.tweets, function(tweets) {
      _.each(tweets, function(tweet) {
        _.forIn(tweet, function(value, key) {
          if (!_.isString(value)) { return; }
          // eval handles \x## and \u##
          // _.unescape handles &###;
          // .replace tries to prevent arbitrary code execution
          tweet[key] = _.unescape(eval('"' + value.replace(/"/g, '\\x22').replace(/\r\n|\n|\r/gm, '\\x0A').replace(/\\/, '\\x5c') + '"'));
        });
      });
    });
    return json;
  }

  var
    query = new Backbone.Model({query: '', topics: 0}),
    drilldown = new (Backbone.Model.extend({
      url: function() { return '/gp/tasa/top_tweets/q?' + $.param({sr_trm: query.get('query')}); },
      parse: parseTweets
    }))(),
    totalTweets = new (TimeSeries.extend({url: function() { return '/gp/tasa/total_tweets/q?sr_trm=' + query.get('query'); }}))(),
    sentimentMapping = new (TimeSeries.extend({url: function() { return '/gp/tasa/sentiment_mapping/q?sr_trm=' + query.get('query'); }}))(),
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
    }))(),
    adjectives = new (Backbone.Collection.extend({
      url: function() { return '/gp/tasa/adjectives/q?sr_trm=' + query.get('query'); },
      comparator: 'normalized_frequency',
      model: Backbone.Model.extend({
        idAttribute: 'word'
      })
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
    }))()
   ;

  $('body').html(JST['templates/application']);
  new DrilldownView({el: $('.drilldown-content'), model: drilldown});
  new TimeSeriesView({el: $('.total-tweets .graph-content'), model: totalTweets});
  new TimeSeriesView({el: $('.sentiment .graph-content'), model: sentimentMapping});
  new HeatmapView({el: $('.tweet-activity .heatmap-content'), model: tweetActivity});
  new TagCloudView({el: $('.adjectives .tag-cloud'), model: adjectives});
  new ForceView({el: $('.topic-cluster .force'), model: force});
  new TagCloudView({el: $('.topic-cluster .tag-cloud'), model: force});

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

    drilldown.clear({silent: true});

    if (_.has(query.changedAttributes(), 'query')) {
      _.invoke(oldXhrRequests, 'abort');
      _.result(forceXhrRequest, 'abort');

      $('body').toggleClass('has-query', Boolean(query.get('query')));
      xhrRequests = _.invoke([totalTweets, drilldown, sentimentMapping, tweetActivity, adjectives], 'fetch', {reset: true, silent: true});
      forceXhrRequest = force.fetch({reset: true, silent: true});
    } else if (_.has(query.changedAttributes(), 'topics')) {
      _.result(forceXhrRequest, 'abort');
      forceXhrRequest = force.fetch({reset: true, silent: true});
    }
  });

  $('body')
    .on('click', '[data-topic]', function(e) {
      $('.topic-cluster')[0].dataset.selected = $(e.currentTarget).data('topic');
      e.stopPropagation();
    })
    .on('click', '.topic-cluster', function() {
      delete $('.topic-cluster')[0].dataset.selected;
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

  PopulateDrilldownBehavior({
    el: $('body'),
    model: drilldown,
    resources: {
      totalTweets: totalTweets,
      sentimentMapping: sentimentMapping,
      tweetActivity: tweetActivity,
      adjectives: adjectives,
      force: force
    }
  });
})();