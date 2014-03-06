function httpGet(theUrl, httpResponseHandler){
	var xmlHttp = new XMLHttpRequest();
	//Make asynchronous GET request			    
	xmlHttp.open( "GET", theUrl, true);
	//When the result comes back from the server.
	xmlHttp.onreadystatechange = httpResponseHandler;
	xmlHttp.send(null);
}	

function httpPOST(theUrl, params) {
	var xmlHttp = null;
	xmlHttp = new XMLHttpRequest();
	//Make asynchronous POST request
	xmlHttp.open( "POST", theUrl, true );
	xmlHttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");		
	//When the result comes back from the server.
	xmlHttp.onreadystatechange = httpResponseHandler;
	xmlHttp.send(params);
}	

function fetchTopicCloud(term,num_topics) {
	 var url = "/gp/topic/fetch/q?sr_trm="+encodeURIComponent(term)+"&num_topics="+encodeURIComponent(num_topics);
         xmlHttp = new XMLHttpRequest();
         xmlHttp.open("GET",url,true);
         xmlHttp.onreadystatechange = httpResponseHandler;
         xmlHttp.send(null);
	 /* Handle results of asynchronous XMLHttpRequests */
	 function httpResponseHandler() {
	    if(xmlHttp.readyState == 4 && xmlHttp.status==200) {
                responseData = JSON.parse(xmlHttp.response);
                //Draw force directed graph
                generateForceDirectedGraph(JSON.parse(responseData['topic_graph']));
                //Show topic word clouds
	        var dash_placeholder = document.getElementById("topic_results");
                dash_placeholder.innerHTML = responseData['topic_cloud_d3_table'];
                //Generate D3 word clouds for topics
                generateTopicCloudsTable(responseData['topic_cloud_d3']);                                                                         
            }
         }
}
