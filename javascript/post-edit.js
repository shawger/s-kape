
$('.post-content-edit').autogrow();


$( "#info-toggle" ).click(function() {
  $( ".post-info-edit" ).toggle();
});

$( "#post-submit" ).click(function() {
  name = $( "#name" ).val();
  title  = $( "#title" ).val();
  date = $( "#date" ).val();
  pic = $( "#pic" ).val();
  color = $( "#color" ).val();
  loc = $( "#location" ).val();
  activity = $( "#activity" ).val();
  tags = $( "#tags" ).val();
  comment = $( "#comment" ).val();
  content = $( "#content" ).val();
  hideHeader = 'false';
  hideTitle = 'false';

  if($( "#hide-header" ).is(":checked")){
    hideHeader = 'true'
  }

  if($( "#hide-title" ).is(":checked")){
    hideTitle = 'true'
  }

  add = "no";

  if (window.location.href.indexOf("admin/post-add") >= 0){
    add = "yes";
  }

  $.post( "/admin/post-update", { name: name,
                                  title: title,
                                  date: date,
                                  pic: pic,
                                  color: color,
                                  location: loc,
                                  activity: activity,
                                  tags: tags,
                                  comment: comment,
                                  content: content,
                                  add: add,
                                  hideHeader: hideHeader,
                                  hideTitle: hideTitle} ).done(function(data){

        if (window.location.href.indexOf("admin/post-add") >= 0){

          if(data == "success"){
           window.location.href = "/posts/"+name;
          }
          else{
            $( "#msg" ).html(data);
          }

        }
        else {
          $( "#msg" ).html(data);
        }

  });
});

$( ".form-group" ).change(function() {
  $( "#msg" ).html("");
});

$( "#content" ).change(function() {
  $( "#msg" ).html("");
});


$( "#post-publish" ).click(function() {

  postName  = $( "#name" ).val();

  $.post( "/admin/post-publish", {name:postName}).done(function(data){

    $( "#msg" ).html(data);

    if(data == "published"){
      $( "#post-publish" ).html("un-publish")
    }

    if(data == "un-published"){
      $( "#post-publish" ).html("publish")
    }

  });
});
