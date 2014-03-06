
//Draw a force directed graph to represent results of the topic graph
function generateForceDirectedGraph(graph) {
        var item = document.getElementById("d3_plots_force_directed_graph");
        item.innerHTML = PLOT_HEADING.replace('#TITLE#',"Force Directed Topic Graph");
	var width = 800,
	    height = 400;

	var color = d3.scale.category10();
        var edge_weight = d3.scale.sqrt()
                              .domain([0,100])
                              .range([0,3]);

	var force = d3.layout.force()
		.charge(-25)
		.linkDistance(50)
		.size([width, height]);

	var svg = d3.select("#d3_plots_force_directed_graph").append("svg")
		.attr("width", width)
		.attr("height", height);

        //Draw a border
        svg.append("rect")
           .attr("width", width)
           .attr("height", height)
           .attr("fill","none")
           .attr("stroke","#FF7C11")
           .attr("stroke-width","5");

	var drawGraph = function(error, graph) {
	  force.nodes(graph.nodes)
	       .links(graph.links)
	       .start();

	  var link = svg.selectAll(".link")
		  .data(graph.links)
		.enter().append("line")
		  .attr("class", "link")
		  .style("stroke-width", function(d) { return edge_weight(d.value); });

	  var node = svg.selectAll(".node")
		  .data(graph.nodes)
		.enter().append("circle")
		  .attr("class", "node")
		  .attr("r", 5)
		  .style("fill", function(d) { return color(d.group); })
		  .call(force.drag);

	  node.append("title")
		  .text(function(d) { return d.name; });

	  force.on("tick", function() {
		link.attr("x1", function(d) { return d.source.x; })
			.attr("y1", function(d) { return d.source.y; })
			.attr("x2", function(d) { return d.target.x; })
			.attr("y2", function(d) { return d.target.y; });

		node.attr("cx", function(d) { return d.x; })
			.attr("cy", function(d) { return d.y; });
	  });
	};

        drawGraph({},graph);
}
