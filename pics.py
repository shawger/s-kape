import webapp2
from datetime import datetime
from google.appengine.ext import ndb
import utils
import colors
import os
import re
from urlparse import urlparse
import logging
from google.appengine.api import users
from google.appengine.api import search

import cloudstorage as gcs
from google.appengine.api import app_identity


import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)



#The storage object
class Pic(ndb.Model):
    
    name = ndb.StringProperty()
    title = ndb.StringProperty()
    date = ndb.DateProperty()
    dateString = ndb.StringProperty()
    pic = ndb.StringProperty()
    location = ndb.StringProperty()
    activity = ndb.StringProperty()
    comment = ndb.StringProperty()
    URL = ndb.StringProperty()
    largeURL = ndb.StringProperty()
    xLargeURL = ndb.StringProperty()
    lowQualityURL = ndb.StringProperty()
    smallURL = ndb.StringProperty()
    thumbURL = ndb.StringProperty()
    publish = ndb.BooleanProperty()
    
    
    def card(self,size):
    
        color = colors.Color.get_by_id("blue")
        
        
        cardTemplate = JINJA_ENVIRONMENT.get_template('/html/card.html')
        
        #Link URL depends if admin
        user = users.get_current_user()
        if users.is_current_user_admin():
            link = '/admin/pics/' + self.name
        else:
            link = '/pics/' + self.name
        
        cardTemplateValues = {
                'name': self.name,
                'title': "",
                'url': "",
                'admin': "",
                'colorOverlay': color.transparent("0.0"),
                'colorOverlayDark': color.transparent("0.1"),
                'picURL': getPicURL(self.name,size),
                'backgroundColor': "#F5F5F5",
                'backgroundColorDark': "#DDD",
                'info': '<b>' + self.title + '</b><br>' + self.comment,
                'cardClass': "pic", 
        }
        
        return cardTemplate.render(cardTemplateValues)
    

def PicCard(name,size):
    
    p = Pic.get_by_id(name)
    
    if (p == None):
        return ""
    
    return p.card(size)
    
class PicList(webapp2.RequestHandler):
    def get(self):
        
        template = JINJA_ENVIRONMENT.get_template('html/cards.html')
        
        templateValues = {
            'queryType': "pic",
        }
        
        pageHTML = template.render(templateValues)
        
        page = utils.ServePage(self)
        page.setColor("blue-grey")
        
        #Add special admin options (will only be shown to admin)
        page.admin = '<li><a href="/admin/pic-add">add</a></li>' \
                     '<li><a href="/admin">admin</a></li>'
       
        #Set metatag data
        page.title = "s-kape | pics"
        page.description = "s-kape.com pics"
        page.img = ""
        page.url = "www.s-kape.com/pics"
                     
        page.write("Pics",pageHTML)


class AddForm(webapp2.RequestHandler):
    def get(self):
        
        #Set up a new Pic
        p = Pic (
            name = "new-pic",
            title = "",
            date = datetime.strptime("2016-01-01", "%Y-%m-%d"),
            dateString = "2016-01-01",
            location = "",
            activity = "",
            comment = "",
            URL = "",
            largeURL = "",
            xLargeURL = "",
            lowQualityURL = "",
            smallURL = "",
            thumbURL = "",
            publish = False,
            
        )
        
        templateValues = {
            'pic': p,
        }
        
        #Load navigation template
        template = JINJA_ENVIRONMENT.get_template('/html/pic-edit.html')
            
        #Create navigation bar using template
        content = template.render(templateValues)
           
        page = utils.ServePage(self)
        page.setColor("grey")
        
        page.admin = '<li><a class="nav-link" id="pic-submit" >save</a></li>'
                     
        
        page.write("new-pic",content)
        
        
class UpdateForm(webapp2.RequestHandler):
    def get(self):
    
        url = urlparse(self.request.url)
        name = url.path.replace("/admin/pics/","")
        p = Pic.get_by_id(name)
        
        if (p == None):
            page = utils.ServePage(self)
            page.write("Error","Page not found")
            
        else:
            templateValues = {
                'pic': p,
            }
            
            #Load navigation template
            template = JINJA_ENVIRONMENT.get_template('/html/pic-edit.html')
                
            #Create navigation bar using template
            content = template.render(templateValues)
            
            page = utils.ServePage(self)
            page.setColor("grey")
            
            page.admin = '<li><a class="nav-link" id="pic-submit" >save</a></li>'
                        
            
            page.write(p.title,content)

      
class View(webapp2.RequestHandler):
    def get(self):
        url = urlparse(self.request.url)
        name = url.path.replace("/pics/","")
        p = Pic.get_by_id(name)
        
        if (p == None):
            page = utils.ServePage(self)
            page.write("Error","Page not found")
        
        else:
            page = utils.ServePage(self)
            
            #Set the color of the page
            page.setColor("grey")
            
            html = '<img src="' + p.URL + '">'
            
            page.write(p.title,html)
            
class PicModal(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name').strip()
        size = self.request.get('size').strip()
        
        if(name == ""):
            self.response.out.write("")
            return
            
        p = Pic.get_by_id(name)
            
        #Oh no. No pic exists
        if(p == None):
            self.response.out.write("")
            return
            
        templateValues = {
            'title': p.title,
            'date': p.dateString,
            'location': p.location,
            'activity': p.activity,
            'comment': p.comment,
            'imgURL': getPicURL(name,size)
        }
        
        #Load navigation template
        template = JINJA_ENVIRONMENT.get_template('/html/pic-modal.html')
        
        self.response.out.write(template.render(templateValues))
  
class Update(webapp2.RequestHandler):
    def post(self):
        
        # Get the stuff from the form
        name = self.request.get('name').strip()
        title = self.request.get('title').strip()
        dateString = self.request.get('date').strip()
        location = self.request.get('location').strip()
        activity = self.request.get('activity').strip()
        comment = self.request.get('comment').strip()
        URL = self.request.get('url').strip()
        largeURL = self.request.get('largeURL').strip()
        xLargeURL = self.request.get('xLargeURL').strip()
        lowQualityURL = self.request.get('lowQualityURL').strip()
        smallURL = self.request.get('smallURL').strip()
        thumbURL = self.request.get('thumbURL').strip()
        add = self.request.get('add').strip()
        
        #first check if the name is valid
        regex = re.compile(ur'^[A-Za-z0-9\-]+$')
        
        if (not re.match(regex, name)):
            self.response.out.write("Name can contain: 'a-z', 'A-Z', '0-9' and '-' only.")
            return
       
        #check if the title is valid. The length should be 20 chars max and not blank
        if(len(title) < 1):
            self.response.out.write("Title cannot be blank")
            return
       
        if(len(title) > 20):
            self.response.out.write("Title is too long. 20 chars max.")
            return
            
            
        #Check if this is an addtion or modification.
        #add will be 'yes' if it is an addition
        
        if(add=="yes"):
            # the title. Make sure it does not already exist
            p = Pic.get_by_id(name)
            
            #Oh no. This already exists
            #Send the message and bail
            if(p != None):
                self.response.out.write(name + " already exists")
                return
        
        if (dateString == ""):
            date = datetime.strptime("2016-01-01", "%Y-%m-%d")
        else:
            try:
                date = datetime.strptime(dateString, "%Y-%m-%d")
                
            except ValueError:
                self.response.out.write("Date format is YYYY-MM-DD")
                return
        
        updatePic = Pic(    name = name,
                            id = name,
                            title = title,
                            date = date,
                            dateString = dateString,
                            location = location,
                            activity = activity,
                            comment = comment,
                            URL = URL,
                            largeURL = largeURL,
                            xLargeURL = xLargeURL,
                            lowQualityURL = lowQualityURL,
                            smallURL = smallURL,
                            thumbURL = thumbURL,
                            publish = True,)
        
                            
        updatePic.put()
        
        addToSearch(updatePic)
        
        self.response.out.write('success')
        

class PicURL(webapp2.RequestHandler):
    def post(self):
        
        name = self.request.get('name').strip()
        size = self.request.get('size').strip()
        
        self.response.out.write(getPicURL(name,size))
        return

def getPicURL(name,size):
    
    if(name == ""):
        return ""
    p = Pic.get_by_id(name)
            
    #Oh no. No pic exists
    if(p == None):
        return ""
     
    if(size=="xLarge"):
        return p.xLargeURL

    if(size=="large"):
        return p.largeURL
       
    if(size=="small"):
         return p.smallURL
            
    if(size=="lowQuality"):
        return p.lowQualityURL
            
    if(size=="thumb"):
        return p.thumbURL
            
    return p.URL
      
def getPic(name):

    logging.info(name)
    return Pic.get_by_id(name)
    
    
#Adds a post to the search libary
def addToSearch(pic):
    
    document = makeSearchDocumet(pic)
    index = search.Index('pics')
    index.delete(pic.name)
    index.put(document)
    
    
def makeSearchDocumet(pic):

    #set up the document
    document = search.Document(
        # Setting the doc_id is optional. If omitted, the search service will
        # create an identifier.
        doc_id=pic.name,
        fields=[
            search.TextField(name='name', value=pic.name),
            search.TextField(name='tName', value=utils.tokenize_word(pic.name)),
            search.TextField(name='title', value=pic.title),
            search.TextField(name='tTitle', value=utils.tokenize_word(pic.title)),
            search.TextField(name='location', value=pic.location),
            search.TextField(name='tLocation', value=utils.tokenize_word(pic.location)),
            search.TextField(name='activity', value=pic.activity),
            search.TextField(name='TActivity', value=utils.tokenize_word(pic.activity)),
            search.TextField(name='comment', value=pic.comment),
            search.DateField(name='date', value=pic.date)
        ])
    
    return document

class ReIndex(webapp2.RequestHandler):
    def get(self): 
    
        index = search.Index('pics')
        
        #Delete all the indexs
        while True:
            # Use ids_only to get the list of document IDs in the index without
            # the overhead of getting the entire document.
            document_ids = [
                document.doc_id
                for document
                in index.get_range(ids_only=True)]

            # If no IDs were returned, we've deleted everything.
            if not document_ids:
                break

            # Delete the documents for the given IDs
            index.delete(document_ids)
            
        #Get all the pics
        allPics = Pic.query()

        #You can only put 200 at a time. So every 200 put the list and clear
        i = 0
        documents = []
        for pic in allPics:
            documents.append(makeSearchDocumet(pic))
            if(i>=199):
                results = index.put(documents)
                documents = []
                i = 0
            else:
                i = i+1
                
        #Add the remaining docs
        results = index.put(documents)
        self.response.out.write('pics re-indexed')

def findCards(query):
    
    picList = ""
    index = search.Index('pics')
            
            
    if(query == ""):
        sort_date= search.SortExpression(
            expression='date',
            direction=search.SortExpression.DESCENDING,
            default_value=0)
        sort_options = search.SortOptions(expressions=[sort_date])
        query_options = search.QueryOptions(
            sort_options=sort_options)
        query = search.Query(query_string=query, options=query_options)  

    documents = index.search(query)
            
    i = 0
    for document in documents:
        if(i==0):
            picList = "pic:" + document.field('name').value
        else:
            picList = picList + ",pic:" +  document.field('name').value
            
        i = i + 1
        
    return picList
    

class PicsInBucket(webapp2.RequestHandler):
    def get(self): 
    
        stats  = gcs.listbucket("/s-kape/pics")
        
        page = utils.ServePage(self)
        page.setColor("grey")
        
        html = ""
        for stat in stats:
            file = stat.filename.lower();
            fileNoPath = file.replace("/s-kape/pics/","")
            if("/" not in fileNoPath and ".jpg" in fileNoPath):
                fileParts = fileNoPath.split(".")
                name = fileParts[0]
                
                #check if name is in data store
                p = Pic.get_by_id(name)
                
                #not here. add it to the list
                
                if(p==None):
                    html = html + '<a href="/admin/pics-bucket/' + name +'">' + name + '</a></br>'
                
        page.write("pics to add",html)
        
        
class AddFromBucketForm(webapp2.RequestHandler):
    def get(self):
        
        url = urlparse(self.request.url)
        name = url.path.replace("/admin/pics-bucket/","")
        
        #Set up a new Pic
        p = Pic (
            name = name,
            title = "",
            date = datetime.strptime("2016-01-01", "%Y-%m-%d"),
            dateString = "2016-01-01",
            location = "",
            activity = "",
            comment = "",
            URL = "https://storage.googleapis.com/s-kape/pics/" + name + ".jpg",
            largeURL = "https://storage.googleapis.com/s-kape/pics/large/" + name + ".jpg",
            xLargeURL = "https://storage.googleapis.com/s-kape/pics/xLarge/" + name + ".jpg",
            lowQualityURL = "https://storage.googleapis.com/s-kape/pics/lowQuality/" + name + ".jpg",
            smallURL = "https://storage.googleapis.com/s-kape/pics/small/" + name + ".jpg",
            thumbURL = "https://storage.googleapis.com/s-kape/pics/thumb/" + name + ".jpg",
            publish = False,
            
        )
        
        templateValues = {
            'pic': p,
        }
        
        #Load navigation template
        template = JINJA_ENVIRONMENT.get_template('/html/pic-edit.html')
            
        #Create navigation bar using template
        content = template.render(templateValues)
           
        page = utils.ServePage(self)
        page.setColor("grey")
        
        page.admin = '<li><a class="nav-link" id="pic-submit" >save</a></li>'
                     
        
        page.write(name,content)