function generateDayHourHeatMap(searchTerm) {
      var div_id = 'd3_plots_dayhour_heatmap';
      var dayhourhmap_holder = document.getElementById(div_id);
      dayhourhmap_holder.innerHTML = LOADING_ICON.replace('#TITLE#',"Tweet Activity - Heatmap");
      var url = "/gp/senti/hmap/q?sr_trm="+encodeURIComponent(searchTerm);

      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open("GET",url,true);
      xmlHttp.onreadystatechange = httpResponseHandler;
      xmlHttp.send(null);
      //Handle results of asynchronous XMLHttpRequests
      function httpResponseHandler() {
          if(xmlHttp.readyState == 4 && xmlHttp.status==200) {
              responseData = JSON.parse(xmlHttp.response);
              renderDayHourHeatMap(div_id,responseData['hmap']);
          }
      }
}

/*
Inspired by : http://bl.ocks.org/tjdecke/5558084
*/
function renderDayHourHeatMap(div_id, hmap) {
      var dayhourhmap_holder = document.getElementById(div_id);
      dayhourhmap_holder.innerHTML = PLOT_HEADING.replace('#TITLE#',"Tweet Activity - Heatmap");
      var margin = {top: 50, right: 50, bottom: 50, left: 50},
		width = 800 - margin.left - margin.right,
		height = 400 - margin.top - margin.bottom,
          gridSize = Math.floor(width / 24),
          legendElementWidth = gridSize*2,
          buckets = 9,
          colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
          days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
          times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];


      //Day ranges from 1 to 7,  hour ranges from 1 to 24.
      var hmap_transformed = hmap.map(function(d){ return { day: +d.day+1, hour: +d.hour+1, value: +d.num_tweets, msi: +d.msi }; });
    
      var drawHeatMap = function(error, hmap_transformed) {
          var colorScale = d3.scale.quantile()
              .domain([0, buckets - 1, d3.max(hmap_transformed, function (d) { return d.value; })])
              .range(colors);

          var svg = d3.select('#'+div_id).append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom);
          
           //Draw a border
           svg.append("rect")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .attr("fill","none")
              .attr("stroke","#FF7C11")
              .attr("stroke-width","5");

          var svg = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

          var dayLabels = svg.selectAll(".dayLabel")
              .data(days)
              .enter().append("text")
                .text(function (d) { return d; })
                .attr("x", 0)
                .attr("y", function (d, i) { return i * gridSize; })
                .style("text-anchor", "end")
                .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
                .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"); });

          var timeLabels = svg.selectAll(".timeLabel")
              .data(times)
              .enter().append("text")
                .text(function(d) { return d; })
                .attr("x", function(d, i) { return i * gridSize; })
                .attr("y", 0)
                .style("text-anchor", "middle")
                .attr("transform", "translate(" + gridSize / 2 + ", -6)")
                .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

          var heatMap = svg.selectAll(".hour")
              .data(hmap_transformed)
              .enter().append("rect")
              .attr("x", function(d) { return (d.hour - 1) * gridSize; })
              .attr("y", function(d) { return (d.day - 1) * gridSize; })
              .attr("rx", 4)
              .attr("ry", 4)
              .attr("class", "hour bordered")
              .attr("width", gridSize)
              .attr("height", gridSize)
              .style("fill", colors[0]);

          heatMap.transition().duration(1000)
              .style("fill", function(d) { return colorScale(d.value); });

          heatMap.append("title").text(function(d) { return d.value; });
              
          var legend = svg.selectAll(".legend")
              .data([0].concat(colorScale.quantiles()), function(d) { return d; })
              .enter().append("g")
              .attr("class", "legend");

          legend.append("rect")
            .attr("x", function(d, i) { return legendElementWidth * i; })
            .attr("y", height)
            .attr("width", legendElementWidth)
            .attr("height", gridSize / 2)
            .style("fill", function(d, i) { return colors[i]; });

          legend.append("text")
            .attr("class", "mono")
            .text(function(d) { return "≥ " + Math.round(d); })
            .attr("x", function(d, i) { return legendElementWidth * i; })
            .attr("y", height + gridSize);
      };
      drawHeatMap({},hmap_transformed);
}