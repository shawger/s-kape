//When the page is first loaded, fill with the correct amount of cards
search()

//A queue for printing cards
var cardsToLoad = new Array();
var cardsRequestedCounter = 0;
var loadingCards = false;


        
//Search will use the query in #query
function search() {
    var query = $( "#search" ).val();
    var queryType = $( "#query-type" ).html();
    
    $.post("/cards/search", {query: query,queryType: queryType}, function(result){
        $("#results").html(result);
        cardsRequestedCounter = 0;
        
        if(result==""){
            $("#cards").html("No results found in " + queryType);
        }
        else{
             $("#cards").html("");
        }
        cardsToLoad = result.split(",");
        
        //If no cards have been loaded. Fill the screen
        if(cardsRequestedCounter == 0){
            cardsOnLoad();
        }
        else{
            loadMoreCards();
        }

    });
}

//Search Button
$( "#search-button" ).click(function() {
    search()
});

$('#search').bind("enterKey",function(e){
    search()
});
$('#search').keyup(function(e){
    if(e.keyCode == 13)
    {
        $(this).trigger("enterKey");
    }
});

//When the user scrolls down. We might want to load more cards
$(window).scroll(function() {
    var scrollHeight = $(window).scrollTop();
    var browserHeight = $(window).height();
    var pageHeight = $( document ).height();
    
    //If the current view is 100px from the bottom, load more cards
    if(scrollHeight + browserHeight > pageHeight - 100 && ! loadingCards){
        
        //Large screen. load 3 cards
        if($( window ).width() >= 767){
            loadCards(3);
        }
        //Small screen. Load 1 card
        else{
            loadCards(1);
        }
    }
});

//When the size of the screen changes we better make sure there are enough cards
$( window ).resize(function() {
    
    var cardsThatShouldBeLoaded = cardsRequiredToFillScreen();
    
    if(cardsThatShouldBeLoaded > cardsRequestedCounter){
        var cardsToLoad = cardsThatShouldBeLoaded - cardsRequestedCounter;
        loadCards(cardsToLoad);
    }
});

//Decides how many new cards to load and request them
function loadMoreCards() {
    var cardNumber;
    
    //Only load cards if there are cards to load
    if (cardsRequestedCounter < cardsToLoad.length){
        
        //Just testing this with 4 for now...
        loadCards(10);
    }
     
}

//Determines how many cards are needed to fill a browser window
function cardsRequiredToFillScreen(){
    var width = $( window ).width();
    var height = $( window ).height();
    var cardWdith = 0;
    //determine width and height of cards (they are squares, so its the same!)
    
    //1000 is the max width of the card holder
    //At over 767 there are 3 cards
    if (width >= 1000){
        cardWdith = 333;
    }
    
    //
    else if(width >= 767){
        cardWdith = width/3;
        
    }
    //cards are equal to browser width
    else{
        cardWdith = width;
    }
    
    //Now we know the amount of cards so lets figure out how many we need (we add 1 row)
    
    rowsToLoad = Math.floor(height/cardWdith) + 1;
    var cardsToLoad = 0;
    
    //If the width is over 767 then there are 3 cards in a row
    if (width >= 767){
        cardsToLoad = 3 * rowsToLoad;
    }
    else{
        cardsToLoad = rowsToLoad;
    }
    
    return cardsToLoad;
}

//Loads cards at the start to match the screen size. Load a little more
//cards then are needed to make sure there is a scroll bar
function cardsOnLoad() {
    
    
    var cardsToLoad = cardsRequiredToFillScreen();
    
    loadCards(cardsToLoad);
}


//Load a specified number of cards
function loadCards(numberOfCards) {
    
    //No cards to load. Lets bail
    if (cardsRequestedCounter >= cardsToLoad.length){
        return
    }
    
    var startIndex = cardsRequestedCounter;
    var endIndex;
    
    //Still enough cards left to load. Load em
    if(cardsRequestedCounter + numberOfCards <= cardsToLoad.length){
        endIndex = cardsRequestedCounter + numberOfCards;
        cardsRequestedCounter = cardsRequestedCounter + numberOfCards;
    }
    
    //We are at the end. Load as many cards as you can
    else{
        endIndex = cardsToLoad.length;
        cardsRequestedCounter = cardsToLoad.length;
    }
    
    var cardsRequested = cardsToLoad.slice(startIndex, endIndex);
    requestString = ""
    for(i=0;i<cardsRequested.length;i++){
        if(i == 0){
            requestString = cardsRequested[i];
        }
        else{
            requestString = requestString + "," + cardsRequested[i];
        }
    }
    
    var cardSize = "normal";
    var width = $( window ).width();
    
    if(width > 1200){
        cardSize = "normal";
    }
    else if(width > 767){
        cardSize = "small";
    }
    else if(width > 400){
        cardSize = "normal";
    }
    else{
        cardSize = "small";
    }
        
    loadingCards = true;
    $.post("/cards/get", {cards: requestString, size: cardSize}, function(result){
        var oldHTML = $("#cards").html();
        $("#cards").html(oldHTML + result);
        $(".card-title").fitText(0.7, { minFontSize: '20px', maxFontSize: '150px' });
        $(".card-content").fitText(1.8, { minFontSize: '14px', maxFontSize: '28px' });
        loadingCards = false;
    });
    
}

