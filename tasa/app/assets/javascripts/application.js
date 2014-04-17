//= require jquery
//= require jquery_ujs
//= require lodash
//= require handlebars.runtime
//= require backbone
//= require rickshaw_with_d3
//= require templates/application
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
     }))()
   ;

  $('body').html(JST['templates/application']);

  $('body').on('submit', '.query', function(e) {
    _.each($(e.currentTarget).serializeArray(), function(input) {
      query.set(input.name, input.value);
    });
    $(document.activeElement).blur();
  });

  $('body').one('webkitTransitionEnd', function() {
    var
      queryNode =  $('.query'),
      threshold = queryNode.offset().top,
      contentTop = $('.graphs').offset().top,
      start = threshold,
      finish = contentTop - queryNode.outerHeight() + 30
      ;
    $(window).scroll(function() {
      var scrollTop = $('body').scrollTop(),
        opacity = Math.min(Math.max((scrollTop - start) / (finish - start), 0), 0.99)
        ;
      queryNode.toggleClass('sticky',  scrollTop > threshold);
      queryNode.css('background-color', queryNode.css('background-color').replace(/[\d.]+(?=\))/, opacity));
    });
  });

  query.on('change:query', function(query, value) {
    $('body').toggleClass('has-query', Boolean(value));
    totalTweets.fetch({reset: true});
  });

  var graph;
  totalTweets.on('reset', function() {
    if (!graph) {
      graph = new Rickshaw.Graph({
        element: $('.total-tweets .graph')[0],
        renderer: 'line',
        height: 300,
        series: [{data: [{x: 0, y: 0}], color: '#fff'}]
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
        tickFormat: function(i) { return d3.time.format.utc('%b %e')(totalTweets.at(i).get('posted_date')); }
      });

      new Rickshaw.Graph.HoverDetail({
        graph: graph,
        formatter: function(series, i, tweets) {
          var point = totalTweets.at(i);
          return '' +
            '<span class="date">' + d3.time.format.utc('%b %e')(point.get('posted_date')) + '</span>' +
            '<span class="tweets">' + point.get('num_tweets') + '</span>' +
            '<span class="units">tweets</span>'
          ;
        }
      });
    }

    graph.series[0].data = totalTweets.toJSON();
    graph.render();
  });
})();