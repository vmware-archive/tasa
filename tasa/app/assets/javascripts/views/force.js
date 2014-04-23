(function() {
  'use strict';
  window.ForceView = SpinnerView.extend({
    template: 'templates/force',

    decorator: function() {
      return {
        topics: _.pluck(_.groupBy(this.model.get('nodes'), 'group'), 'length')
      };
    },

    render: function(options) {
      var self = this;
      SpinnerView.prototype.render.call(this, options);
      if (options.loading) { return; }

      var data = this.model.toJSON();
      var $svg = this.$('svg');
      var width = $svg.width(),
          height = $svg.height();

      var edge_weight = d3.scale.sqrt()
        .domain([0,100])
        .range([0,3]);

      var force = d3.layout.force()
        .charge(-25)
        .linkDistance(50)
        .size([width, height]);

      var d3svg = d3.select($svg[0]);

      force
        .nodes(data.nodes)
        .links(data.links)
      ;

      var link = d3svg.selectAll('.link')
        .data(data.links).enter()
        .append('line')
          .attr('class', 'link');

      var node = d3svg.selectAll('.node')
        .data(data.nodes).enter()
        .append('circle')
          .attr('class', function(d) { return 'node t' + d.group; })
          .attr('r', 5)
      ;

      node.append('title')
        .text(function(d) { return d.name; });

      force.start();
      _.times(300, force.tick);
      force.stop();

      link
        .attr('x1', function(d) { return d.source.x; })
        .attr('y1', function(d) { return d.source.y; })
        .attr('x2', function(d) { return d.target.x; })
        .attr('y2', function(d) { return d.target.y; })
      ;

      node
        .attr('cx', function(d) { return d.x; })
        .attr('cy', function(d) { return d.y; })
      ;
    }
  });
})();