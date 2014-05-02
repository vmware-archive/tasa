//= require jquery
//= require jquery_ujs
//= require lodash
//= require handlebars.runtime
//= require backbone
//= require rickshaw_with_d3
//= require cal-heatmap
//= require d3.layout.cloud
//= require_tree ./collections
//= require_tree ./templates
//= require views/spinner
//= require_tree ./views
//= require_tree ./behaviors
//= require bootstrap/tooltip
(function() {
  'use strict';

  /* Entities */
  var
    query = new Backbone.Model({query: '', topics: 0}),
    drilldown = new (Backbone.Model.extend({
      url: urlFor('top_tweets'),
      parse: parseTweets
    }))(),
    totalTweets = new (TimeSeries.extend({url: urlFor('total_tweets')}))(),
    sentimentMapping = new (TimeSeries.extend({url: urlFor('sentiment_mapping')}))(),
    tweetActivity = new (Backbone.Collection.extend({
      url: urlFor('tweet_activity'),
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
      url: urlFor('adjectives'),
      comparator: 'normalized_frequency',
      model: Backbone.Model.extend({idAttribute: 'word'})
     }))(),
    force = new (Backbone.Model.extend({
      url: urlFor('topic_cluster'),
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

  /* Dependencies */
  var
    $body = $('body'),
    resources = {
      drilldown: drilldown,
      totalTweets: totalTweets,
      sentimentMapping: sentimentMapping,
      tweetActivity: tweetActivity,
      adjectives: adjectives,
      force: force
    }
  ;

  /* Template Rendering */
  $body.html(JST['templates/application']);
  new DrilldownView({el: $body.find('.drilldown-content'), model: drilldown});
  new TimeSeriesView({el: $body.find('.total-tweets .graph-content'), model: totalTweets});
  new TimeSeriesView({el: $body.find('.sentiment .graph-content'), model: sentimentMapping});
  new HeatmapView({el: $body.find('.tweet-activity .heatmap-content'), model: tweetActivity});
  new TagCloudView({el: $body.find('.adjectives .tag-cloud'), model: adjectives});
  new ForceView({el: $body.find('.topic-cluster .force'), model: force});
  new TagCloudView({el: $body.find('.topic-cluster .tag-cloud'), model: force});

  /* Behaviors */
  ScrollTransitionBehavior({el: $body});
  SubmitQueryBehavior({el: $body, model: query, resources: resources});
  MarkSelectedTopicBehavior({el: $body});
  MarkChangedFormsBehavior({el: $body});
  PopulateDrilldownBehavior({el: $body, model: drilldown, resources: resources});

  /* Helpers */
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

  function urlFor(name) {
    return function() {
      return '/gp/tasa/' + name + '/q?' + $.param({
        sr_trm: query.get('query'),
        num_topics: query.get('topics')
      });
    };
  }
})();