(function() {
  'use strict';

  window.TagCloudView = SpinnerView.extend({
    render: function(options) {
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var
        filtered_words = _.map(_.invoke(this.model.last(100), 'toJSON'), function(d) {
          return {
            text: d.word
              .replace(/[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g,"")
              .replace(/[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g,""),
            size: 5+ d.normalized_frequency * 150
          };
        }),
        width = $('.adjectives').width(),
        height = 300
      ;

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
})();