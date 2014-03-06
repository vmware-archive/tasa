
/*
Srivatsan Ramanujam<sramanujam@gopivotal.com>
Draw word clouds to depic the topic dashboard
Based on example code by Jason Davies.
*/


/*
Iterate through the JSON object ,where each key represents a topic number and each value is a dict containing an ID and a word_freq_list.
*/
function generateTopicCloudsTable(topic_cloud_json) {
    for (var topic in topic_cloud_json)
    {
        renderWordCloud(topic_cloud_json[topic].word_freq_list,topic_cloud_json[topic].id, 600, 400);
    }
}


function renderWordCloud(word_freq_list,topic_cloud_id, width, height) {
  var fontFamily = "Georgia";
  var fill = d3.scale.category10();
  //To make the word clouds look prettier, remove punctuations & word separators.
  var punct = /[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g;
  var wordsep = /[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g;

  var filtered_words = word_freq_list.map(
                function(d) {
                     //The size is in px units. Since the frequency is normalized, the most frequently occurring word will have a frequency of 1.0 and 
                     //the rest will be normalized by this.
                     return {
                           text: d.word.replace(punct,"").replace(wordsep,""), 
                           // Find y,a such that y^a = min desired font size and y^(a+1) = max desired font size.
                           //size: Math.pow(14,(1.0+d.normalized_frequency)) 
                           size: 5+ d.normalized_frequency*150
                     };
                });

  d3.layout.cloud().size([width, height])
      .words(filtered_words)
      .padding(5)
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .font(fontFamily)
      .fontSize(function(d) { return d.size; })
      .on("end", draw)
      .start();
  /* The argument to the draw function is the "words" attribute which was set during initialization of the d3 cloud layout.*/
  function draw(words) {
     var tCloudElem = "#"+topic_cloud_id;
     d3.select(tCloudElem)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate("+width/2+","+height/2+")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { 
                                 return d.size + "px"; 
                            }
         )
        .style("font-family", fontFamily)
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { 
                       return d.text; 
              });
   }
}