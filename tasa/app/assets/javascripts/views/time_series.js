(function() {
  'use strict';
  window.TimeSeriesView = SpinnerView.extend({
    template: 'templates/time_series',

    render: function(options) {
      var self = this;
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var graph = new Rickshaw.Graph({
        element: this.$('.graph')[0],
        renderer: 'line',
        height: 300,
        series: this.model.toJSON()
      });

      new Rickshaw.Graph.Axis.Y({
        element: this.$('.y-axis-left')[0],
        graph: graph,
        orientation: 'left',
        width: 40,
        height: 300,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT
      });

      new Rickshaw.Graph.Axis.Y({
        element: this.$('.y-axis-right')[0],
        graph: graph,
        orientation: 'right',
        width: 40,
        height: 300,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT
      });

      new Rickshaw.Graph.Axis.X({
        element: this.$('.x-axis')[0],
        graph: graph,
        orientation: 'bottom',
        tickFormat: function(i) { return d3.time.format.utc('%B %e')(self.model.at(i).get('posted_date')); }
      });

      new Rickshaw.Graph.HoverDetail({
        graph: graph,
        formatter: function(series, i, tweets) {
          return '' +
            '<div style="color:' + series.color + '">' +
              '<span class="date">' + d3.time.format.utc('%B %e')(self.model.at(i).get('posted_date')) + '</span>' +
              '<span class="tweets">' + series.data[i].y + '</span>' +
              '<span class="units">tweets</span>' +
            '</div>'
            ;
        }
      });

      new Rickshaw.Graph.Legend({
        element: this.$('.legend')[0],
        graph: graph
      });

      graph.render();
    }
  });
})();