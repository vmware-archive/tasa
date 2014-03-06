
//Time series plots
function fetchTweetsOverTime(searchTerm){
     var url = "/gp/topic/ts/q?sr_trm="+encodeURIComponent(searchTerm);
     var item = document.getElementById("d3_plots_time_series");
     item.innerHTML = LOADING_ICON.replace('#TITLE#',"Tweets Over Time");

     var xmlHttp = new XMLHttpRequest();
     xmlHttp.open("GET",url,true);
     xmlHttp.onreadystatechange = httpResponseHandler;
     xmlHttp.send(null);
     /* Handle results of asynchronous XMLHttpRequests */
     function httpResponseHandler() {
         if(xmlHttp.readyState == 4 && xmlHttp.status==200) {
             responseData = JSON.parse(xmlHttp.response);
             displayLineChart(responseData['tseries']);
         }
     }
}

function displayLineChart(data) {
        
        var item = document.getElementById("d3_plots_time_series");
        item.innerHTML =  PLOT_HEADING.replace('#TITLE#',"Tweets Over Time");

	var margin = {top: 20, right: 50, bottom: 60, left: 50},
		width = 800 - margin.left - margin.right,
		height = 400 - margin.top - margin.bottom;

	var parseDate = d3.time.format("%Y-%m-%d").parse;

	var x = d3.time.scale()
		.range([0, width]);

	var y = d3.scale.linear()
		.range([height, 0]);

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
		.y(function(d) { return y(d.num_tweets); });

	var svg = d3.select("#d3_plots_time_series").append("svg")
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

	var populateTimeSeriesData = function(error, data) {
	  data.forEach(function(d) {
		d.posted_date = parseDate(d.posted_date);
                var parsed_dt = d.posted_date;
	  });

	  x.domain(d3.extent(data, function(d) { return d.posted_date; }));
	  y.domain(d3.extent(data, function(d) { return d.num_tweets; }));

	  svg.append("g")
		  .attr("class", "x axis")
		  .attr("transform", "translate(0," + height + ")")
		  .call(xAxis)
                  .selectAll("text")
                  .style("text-anchor", "end")
		  .attr("transform", "rotate(-60)");

	  svg.append("g")
		  .attr("class", "y axis")
		  .call(yAxis)
		.append("text")
		  .attr("transform", "rotate(-90)")
		  .attr("y", 6)
		  .attr("dy", ".71em")
		  .style("text-anchor", "end")
		  .text("No. of matching tweets");

	  svg.append("path")
		  .datum(data)
		  .attr("class", "line")
		  .attr("d", line);

	}
        populateTimeSeriesData({},data);
}

