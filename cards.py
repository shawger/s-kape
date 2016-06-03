import webapp2
import posts
import pics

from google.appengine.api import search
from google.appengine.api import users

#Handlers search request for cards
#Cards can be of many types
#Cards will be returned sperated by commas. <type>:<name> 
class Search(webapp2.RequestHandler):
    def post(self):
        
        # Get the stuff from the form
        query = self.request.get('query').strip()
        queryType = self.request.get('queryType').strip()
        
        #Common queries will be for all of a certian type
        #We don't need anything real special to handle that id say
        
        #Return all the posts
        if(queryType == "post"):
            
            self.response.out.write(posts.findCards(query))
            return
       
        if(queryType == "pic"):
            
            self.response.out.write(pics.findCards(query))
            return
                                
            
        
        #Nothing found
        self.response.out.write("No matches found.")
        return
        
#Ajax request. I bunch of request for cards will be sent
#This responds with a bunch of cards!
class Get(webapp2.RequestHandler):
    def post(self):
        
        # Get the stuff from the form
        cards = self.request.get('cards').strip()
        size = self.request.get('size').strip()
        
        cardArray = cards.split(",")
        
        resultHTML = ""
        
        for card in cardArray:
            
            resultHTML = resultHTML + getCard(card,size)
           
        self.response.out.write(resultHTML)
        return
        
            
# Card requests should be in 2 parts:
# <type>:<name>        
def getCard(card,size):

    cardParts = card.split(":")
    
    if (len(cardParts) == 2):
        type = cardParts[0]
        name = cardParts[1]
    
        if (type == "post"):
            return posts.PostCard(name,size)
            
        if (type == "pic"):
            return pics.PicCard(name,size)

        
        
        