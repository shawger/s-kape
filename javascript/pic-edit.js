


$( "#url" ).keyup(function() {
    if ($( "#autofill" ).is(':checked') ){
        updateURLs();
    }
});

$( "#pic-submit" ).click(function() {
  var name = $( "#name" ).val();
  var title  = $( "#title" ).val();
  var date = $( "#date" ).val();
  var loc = $( "#location" ).val();
  var activity = $( "#activity" ).val();
  var comment = $( "#comment" ).val();
  var url = $( "#url" ).val();
  var xLargeURL = $( "#xLargeURL" ).val();
  var largeURL = $( "#largeURL" ).val();
  var lowQualityURL = $( "#lowQualityURL" ).val();
  var smallURL = $( "#smallURL" ).val();;
  var thumbURL = $( "#thumbURL" ).val();
  
  $.post( "/admin/pic-update", { name: name, 
                                  title: title,
                                  date: date,
                                  location: loc,
                                  activity: activity,
                                  comment: comment,
                                  url: url,
                                  xLargeURL: xLargeURL,
                                  largeURL: largeURL,
                                  lowQualityURL: lowQualityURL,
                                  smallURL: smallURL,
                                  thumbURL : thumbURL,
                                  add: "no"} ).done(function(data){
        
        $( "#msg" ).html(data);
  });
  
});

function updateURLs() {
    
    var baseURL = $( "#url" ).val()
    
    //Its probably an address
    if(baseURL.indexOf("/") > -1) {
        
        //Split the parts
        var parts = baseURL.split("/");
        
        var end = parts[parts.length - 1];
        
        var basePath = baseURL.replace(end, "");
        
        //If it is a file name remove the end for the file name
        if(end.indexOf(".") > -1){
            var nameParts = end.split(".");
            var name = nameParts[0];
            $( "#name" ).val(name);
        }
        
        var xLargeURL = basePath + "xLarge/" + end;
        var largeURL = basePath + "large/" + end;
        var lowQualityURL = basePath + "lowQuality/" + end;
        var smallURL = basePath + "small/" + end;
        var thumbURL = basePath + "thumb/" + end;
        
        $( "#xLargeURL" ).val(xLargeURL);
        $( "#largeURL" ).val(largeURL);
        $( "#lowQualityURL" ).val(lowQualityURL);
        $( "#smallURL" ).val(smallURL);
        $( "#thumbURL" ).val(thumbURL);
        
        $("#img").attr("src",baseURL);
        
    }
}