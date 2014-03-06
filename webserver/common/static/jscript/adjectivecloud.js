/*
Srivatsan Ramanujam<sramanujam@gopivotal.com>
Draw word clouds to depic the topic dashboard
Based on example code by Jason Davies.
*/

function generateAdjectiveCloud(searchTerm) {
    var adjCloudHolder = document.getElementById("d3_plots_adjective_cloud");
    var url = "/gp/senti/acloud/q?sr_trm="+encodeURIComponent(searchTerm);
    adjCloudHolder.innerHTML = LOADING_ICON.replace('#TITLE#',"Adjectives Tag Cloud");
    
     var xmlHttp = new XMLHttpRequest();
     xmlHttp.open("GET",url,true);
     xmlHttp.onreadystatechange = httpResponseHandler;
     xmlHttp.send(null);
     //Handle results of asynchronous XMLHttpRequests
     function httpResponseHandler() {
         if(xmlHttp.readyState == 4 && xmlHttp.status==200) {
             responseData = JSON.parse(xmlHttp.response);
             displayAdjectiveCloud(responseData['adjective_cloud']);
         }
     }
}

function displayAdjectiveCloud(adjectiveCloudDict) {
     var item = document.getElementById('d3_plots_adjective_cloud');
     item.innerHTML = PLOT_HEADING.replace('#TITLE#','Adjectives Tag Cloud');
     renderWordCloud(adjectiveCloudDict, 'd3_plots_adjective_cloud', 800, 400);
}