(function() {
  'use strict';
  window.HeatmapView = SpinnerView.extend({
    template: 'templates/heatmap',

    render: function(options){
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var cellSize = this.$el.width() / 24 - 2 + .25 - 60/24,
          data = this.model.toJSON(),
          labelWidth = 60;

      new CalHeatMap().init({
        itemSelector: this.$('.heatmap').selector,
        domain: 'day',
        subDomain: 'hour',
        range: 7,
        data: this.model.toJSON(),
        start: new Date(2013, 5, 31),
        colLimit: 24,
        verticalOrientation: true,
        cellSize: cellSize,
        considerMissingDataAsZero: true,
        domainLabelFormat: '%a',
        label: {position: 'left', align: 'right', width: labelWidth},
        domainMargin: -2,
        tooltip: true,
        subDomainTitleFormat: {empty: '{date}', filled: '{date}'},
        subDomainDateFormat: function(date) {
          return (data[Number(date) / 1000] || 0) + ' Tweets';
        },
        displayLegend: false
      });

      this.$el.append('<style>.ch-tooltip {margin-top: ' + cellSize / 2 + 'px;' + ' margin-left: ' + (labelWidth - 2) + 'px;}</style>');
    }
  });
})();