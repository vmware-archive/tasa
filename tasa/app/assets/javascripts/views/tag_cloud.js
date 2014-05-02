(function() {
  'use strict';

  window.TagCloudView = SpinnerView.extend({
    render: function(options) {
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var
        self = this,
        data = this.model.toJSON(),
        width = this.$el.width(),
        height = 400
      ;

      _.each(data, function(word) {
        word.text = word.word
          .replace(/[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g, "")
          .replace(/[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g, "");
      });

      var el = this.el,
          frequencies = _.pluck(data, 'normalized_frequency'),
          scale = d3.scale.linear()
            .domain(_.invoke([_.min, _.max], 'call', undefined, _.pluck(data, 'normalized_frequency')))
            .range([14, 50]);
      d3.layout.cloud()
        .size([width, height])
        .words(data)
        .text(function(d) { return d.text; })
        .padding(5)
        .rotate(0)
        .font('Open Sans')
        .fontSize(function(d) { return scale(d.normalized_frequency); })
        .spiral('archimedean')
        .on('end', function(words) {
          d3.select(el)
            .append('svg')
              .attr('width', width)
              .attr('height', height)
              .append('g')
                .attr('transform', 'translate(' + width / 2 + ', ' + height / 2 + ')')
                .selectAll('text')
                .data(words).enter()
                .append('text')
                  .attr('class', function(d) { return 't' + d.topic; })
                  .attr('transform', function(d) { return 'translate(' + [d.x, d.y] + ')'; })
                  .attr('data-topic', function(d) { return d.topic; })
                  .attr('data-adjective', function(d) { return d.text; })
                  .attr('data-toggle', 'tooltip')
                  .attr('title', function(d) {
                    var total = _.reduce(_.pluck(data, 'normalized_frequency'), function(sum, freq){return sum+freq;}, 0);
                    return '<div class="tweet-percentage">' + (100 * d.normalized_frequency / total).toFixed(2) + '%</div> of tweets';
                  })
                  .append('tspan')
                    .style('font-size', function(d) { return d.size + 'px'; })
                    .style('font-family', 'Open Sans')
                    .style('opacity', function(d) { return Math.sqrt(d.normalized_frequency); })
                    .text(function(d) { return d.text; })
          ;

          self.$('text')
            .tooltip({container: 'body', placement: 'top', html: true})
            .on('shown.bs.tooltip', function() { $('.tooltip').addClass('cloud-tooltip'); })
          ;
        })
        .start();
    }
  });
})();