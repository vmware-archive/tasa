//= require jquery
//= require jquery_ujs
//= require lodash
//= require handlebars.runtime
//= require backbone
//= require rickshaw_with_d3
//= require d3.layout.cloud
//= require_tree ./templates
//= require views/spinner
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
       toJSON: function() { return this.map(function(model, i) { return _.extend(model.toJSON(), {x: i}); }); }
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
     adjectives = new (Backbone.Collection.extend({
       url: function() { return '/gp/senti/acloud/q?sr_trm=' + query.get('query'); },
       parse: function(response) { return response.adjective_cloud; },
       comparator: 'normalized_frequency'
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
  var totalTweetsView = new SpinnerView({
    el: $('.total-tweets .graph-content'),
    template: 'templates/total_tweets',
    model: totalTweets,
    render: function(options) {
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var graph = new Rickshaw.Graph({
        element: $('.total-tweets .graph')[0],
        renderer: 'line',
        height: 300,
        series: [{data: totalTweets.toJSON(), color: '#fff'}]
      });

      new Rickshaw.Graph.Axis.Y({
        element: $('.total-tweets .y-axis-left')[0],
        graph: graph,
        orientation: 'left',
        width: 40,
        height: 300,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT
      });

      new Rickshaw.Graph.Axis.Y({
        element: $('.total-tweets .y-axis-right')[0],
        graph: graph,
        orientation: 'right',
        width: 40,
        height: 300,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT
      });

      new Rickshaw.Graph.Axis.X({
        element: $('.total-tweets .x-axis')[0],
        graph: graph,
        orientation: 'bottom',
        tickFormat: function(i) { return d3.time.format.utc('%B %e')(totalTweets.at(i).get('posted_date')); }
      });

      new Rickshaw.Graph.HoverDetail({
        graph: graph,
        formatter: function(series, i, tweets) {
          var point = totalTweets.at(i);
          return '' +
            '<span class="date">' + d3.time.format.utc('%B %e')(point.get('posted_date')) + '</span>' +
            '<span class="tweets">' + point.get('num_tweets') + '</span>' +
            '<span class="units">tweets</span>'
            ;
        }
      });

      graph.render();
    }
  });
  var adjectivesView = new SpinnerView({
    el: $('.adjectives .tag-cloud'),
    model: adjectives,
    render: function(options) {
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var
        filtered_words = _.map(_.invoke(adjectives.last(100), 'toJSON'), function(d) {
          return {
            text: d.word
              .replace(/[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g,"")
              .replace(/[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g,""),
            size: 5+ d.normalized_frequency * 150
          };
        }),
        width = $('.adjectives').width(),
        height = 300;

      d3.layout.cloud()
        .size([width, height])
        .words(filtered_words)
        .text(function(d) { return d.text; })
        .padding(5)
        .rotate(0)
        .font('Open Sans')
        .fontSize(function(d) { return d.size; })
        .spiral('rectangular')
        .on('end', function(words) {
          d3.select('.adjectives .tag-cloud')
            .append('svg')
              .attr('width', width)
              .attr('height', height)
              .append('g')
                .attr('transform', 'translate(' + width / 2 + ', ' + height / 2 + ')')
                .selectAll('text')
                .data(words).enter()
                .append('text')
                  .style('font-size', function(d) { return d.size + 'px'; })
                  .attr('transform', function(d) { return 'translate(' + [d.x, d.y] + ')'; })
                  .text(function(d) { return d.text; })
          ;
        })
        .start();
    }
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
    _.invoke([totalTweets, sideBar, adjectives], 'fetch', {reset: true});
  });
})();