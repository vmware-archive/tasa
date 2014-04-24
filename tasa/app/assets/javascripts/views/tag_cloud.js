(function() {
  'use strict';

  window.TagCloudView = SpinnerView.extend({
    render: function(options) {
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var
        data = this.model.toJSON(),
        width = this.$el.width(),
        height = 400
      ;

      _.each(data, function(word) {
        word.text = word.word
          .replace(/[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g, "")
          .replace(/[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g, "");
        word.size = 5 + word.normalized_frequency * ((data.length > 90) ? 150 : 70);
      }, this);

      var el = this.el;
      d3.layout.cloud()
        .size([width, height])
        .words(data)
        .text(function(d) { return d.text; })
        .padding(5)
        .rotate(0)
        .font('Open Sans')
        .fontSize(function(d) { return d.size; })
        .spiral('rectangular')
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
                  .style('font-size', function(d) { return d.size + 'px'; })
                  .attr('transform', function(d) { return 'translate(' + [d.x, d.y] + ')'; })
                  .text(function(d) { return d.text; })
          ;
        })
        .start();
    }
  });
})();