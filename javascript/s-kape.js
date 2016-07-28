//Common script for s-kape site. Pic loading and scrolling
window.onload = deferImageLoader;
$(document).on('click', '.pic', picModal);
$(document).on('click', '.modal-close', closeModal);
$(document).on('click', '.modal-right', picModal);
$(document).on('click', '.modal-left', picModal);

currentWidth = $( window ).width();


$(".ftLarge").fitText(0.9, { minFontSize: '28px', maxFontSize: '120px' });
$(".ftSmall").fitText(1.8, { minFontSize: '16px', maxFontSize: '30px' });
$(".card-title").fitText(0.7, { minFontSize: '20px', maxFontSize: '150px' });
$(".card-info").fitText(1.8, { minFontSize: '18px', maxFontSize: '28px' });


$(window).scroll(function() {

    if($( window ).width() > 767){
        $(".navbar-text").show();
    }
});

function deferImageLoader() {

    $('#header').css("background","url=https://storage.googleapis.com/s-kape/pics/kia.jpg")

    var imgDefer = document.getElementsByClassName('inline-img');
    for (var i=0; i<imgDefer.length; i++) {
        getPic(imgDefer[i].getAttribute('id'),"inline-img");
    }
}

$("#scroll").click(function() {
    $('html, body').animate({
        scrollTop: $("#scroll").offset().top
    }, 500);
});

function getPic(picName, picType){

    //Defualt max width
    var maxWidth = 1000;

    var screenWidth = $( window ).width();

    //Determine the size of the picture to grab
    if(picType == "full"){
        maxWidth = screenWidth;
    }

    if(picType == "header"){
        maxWidth = screenWidth;
    }

    if(picType == "inline-img"){

        if(screenWidth >= 800){
            maxWidth = 800;
        }
        else{
            maxWidth = screenWidth;
        }
    }

    if(picType == "card"){

        if(screenWidth >= 1000){
            maxWidth = 333;
        }
        else if (screenWidth >= 767){
            maxWidth = math.floor(screenWidth/3);
        }
        else{
            maxWidth = screenWidth;
        }

    }

    var picSize = "normal";

    //from the picture size, request the correct size.
    if(maxWidth>1920){
        picSize = "xLarge"
    }
    else if(maxWidth>800){
        picSize = "large";
    }
    else if(maxWidth>400){
        picSize = "normal";
    }
    else{
        picSize = "small";
    }

    $.post("/pics-url", {name: picName,size: picSize}, function(result){
        var url = result;
        $("."+ picType + "#" + picName ).attr("src", result);
    });

    var screenWidth = $(this).attr('src');

}

function picModal(){
    var picName = $(this).attr('id');

    if(!detectIE()){
        showPicModal(picName);
    }
}

function closeModal(){
    $('#picModal').modal('hide')
}
function showPicModal(picName){

    var screenWidth = $( window ).width();

    var picSize = "normal";

    //from the picture size, request the correct size.
    if(screenWidth>1920){
        picSize = "xLarge"
    }
    else if(screenWidth>800){
        picSize = "large";
    }
    else if(screenWidth>400){
        picSize = "normal";
    }
    else{
        picSize = "small";
    }


    $.post("/pics-modal", {name: picName,size: picSize}, function(result){
        var modal = result;
        $(".modal" ).html(modal);
        modalLeftAndRight(picName);
        setModalMaxWidth();

    });


    $('#picModal').modal('show');
}

function modalLeftAndRight(picName){

    if($('#results').length && $('#results').html() != "" ){
        var picList = $('#results').html();
        var pics = picList.split(",");

        var picIndex = pics.indexOf("pic:"+picName);

        if(picIndex < 1){
            $('.modal-left').hide();
        }
        else{
            $('.modal-left').show();
            var leftItem = pics[picIndex-1].replace("pic:","");
            $('.modal-left').attr("id",leftItem);
        }
        if(picIndex + 1 == pics.length)
        {
            $('.modal-right').hide();
        }
        else{
            $('.modal-right').show();
            var rightItem = pics[picIndex+1].replace("pic:","");
            $('.modal-right').attr("id",rightItem);
        }
    }
    else{
        $('.modal-right').hide();
        $('.modal-left').hide();
    }

}



//Set max width of the modal according to picture in the modal
function setModalMaxWidth() {

    //the images are 4:3
    var headerHeight  = $('.modal-header').outerHeight() || 0;
    var footerHeight  = $('.modal-footer').outerHeight() || 0;
    var picHeight = $('.modal-image').outerHeight() || 0;
    var picWidth = $('.modal-image').outerWidth() || 0;

    //asume 4/3
    var ration = 1;
    if(picHeight == 0 || picWidth == 0){
        ratio = 3.9/3;
    }
    else{
        ratio = picWidth/picHeight;
    }



    var maxImgHeight = $( window ).height() - headerHeight - footerHeight - 70;


    var maxWidth = Math.floor(maxImgHeight * ratio);

     $('.modal-dialog').css({
        'max-width': maxWidth
     });


}

//Things to do when the windows changes
$(window).resize(function() {
  if ($('.modal.in').length != 0) {
    setModalMaxWidth();
  }

  //Check if the screen grows
  if(currentWidth < $( window ).width()){

      //If the screen goes over 400, then we probably need to reload images
      if($( window ).width() > 400){
          deferImageLoader();
      }
  }

  currentWidth = $( window ).width();
});

/**
 * detect IE
 * returns version of IE or false, if browser is not Internet Explorer
 */
function detectIE() {
  var ua = window.navigator.userAgent;

  // Test values; Uncomment to check result …

  // IE 10
  // ua = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)';

  // IE 11
  // ua = 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko';

  // Edge 12 (Spartan)
  // ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0';

  // Edge 13
  // ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586';

  var msie = ua.indexOf('MSIE ');
  if (msie > 0) {
    // IE 10 or older => return version number
    return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
  }

  var trident = ua.indexOf('Trident/');
  if (trident > 0) {
    // IE 11 => return version number
    var rv = ua.indexOf('rv:');
    return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
  }

  var edge = ua.indexOf('Edge/');
  if (edge > 0) {
    // Edge (IE 12+) => return version number
    return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
  }

  // other browser
  return false;
}

$("#search-toggle").click(function(){
    if ($(".search-box").css("display") == "none"){
        $(".search-box").css("display", "table");
    }
    else {
        $(".search-box").css("display", "none");
    }

    $("#navbar").removeClass('in');
    $("#navbar").addClass('out');
});
