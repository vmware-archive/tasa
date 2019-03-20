/*
Modified example from https://bl.ocks.org/mbostock/3884955
*/
function generateMultiSeriesSentimentPlot(searchTerm) {
    var multiSeriesHolder = document.getElementById("d3_plots_multi_series");
    var url = "/gp/senti/ms/q?sr_trm="+encodeURIComponent(searchTerm);
    multiSeriesHolder.innerHTML = LOADING_ICON.replace('#TITLE#',"Sentiment Over Time");;
    
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET",url,true);
    xmlHttp.onreadystatechange = httpResponseHandler;
    xmlHttp.send(null);
    //Handle results of asynchronous XMLHttpRequests
    function httpResponseHandler() {
        if(xmlHttp.readyState == 4 && xmlHttp.status==200) {
            responseData = JSON.parse(xmlHttp.response);
            displayMultiSeriesSentimentPlot(responseData['multi_series']);
        }
    }
}

function displayMultiSeriesSentimentPlot(data) {

    var item = document.getElementById("d3_plots_multi_series");
    item.innerHTML = PLOT_HEADING.replace('#TITLE#',"Sentiment Over Time");

    var margin = {top: 20, right: 100, bottom: 60, left: 50},
		width = 800 - margin.left - margin.right,
		height = 400 - margin.top - margin.bottom;

    var parseDate = d3.time.format("%Y-%m-%d").parse;

    var x = d3.time.scale()
	.range([0, width]);

    var y = d3.scale.linear()
	.range([height, 0]);

    var color = d3.scale.category10()
                .range(["red","blue","green"]);

    var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom")
        .tickFormat(d3.time.format("%d-%b"));

    var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left");

    var line = d3.svg.line()
	.interpolate("basis")
	.x(function(d) { return x(d.posted_date); })
	.y(function(d) { return y(d.tweet_count); });

    var svg = d3.select("#d3_plots_multi_series").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom);

    //Draw a border
    svg.append("rect")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	    .attr("fill","none")
	    .attr("stroke","#FF7C11")
	    .attr("stroke-width","5");

    var svg = svg.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var populateMultiSeriesData = function (error, data) {

	    color.domain(d3.keys(data[0]).filter(function(key) { return key !== "posted_date"; }).sort());

	    data.forEach(function(d) {
	      d.posted_date = parseDate(d.posted_date);
	    });

	    var sentiment_categories = color.domain().map(function(name) {
	      return {
		name: name,
		values: data.map(function(d) {
		  return {posted_date: d.posted_date, tweet_count: +d[name]};
		})
	      };
	    });

	    x.domain(d3.extent(data, function(d) { return d.posted_date; }));

	    y.domain([
	      d3.min(sentiment_categories, function(c) { return d3.min(c.values, function(v) { return v.tweet_count; }); }),
	      d3.max(sentiment_categories, function(c) { return d3.max(c.values, function(v) { return v.tweet_count; }); })
	    ]);

	    svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	    svg.append("g")
		.attr("class", "y axis")
		.call(yAxis)
	      .append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("#Tweets");

	    var sentiment_category = svg.selectAll(".sentiment_category")
		.data(sentiment_categories)
	      .enter().append("g")
		.attr("class", "sentiment_category");

	    sentiment_category.append("path")
		.attr("class", "line")
		.attr("d", function(d) { return line(d.values); })
		.style("stroke", function(d) { return color(d.name); });

	    sentiment_category.append("text")
		.datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
		.attr("transform", function(d) { return "translate(" + x(d.value.posted_date) + "," + y(d.value.tweet_count) + ")"; })
		.attr("x", 3)
		.attr("dy", ".35em")
		.text(function(d) { return d.name; });
    };
    populateMultiSeriesData({},data);
}