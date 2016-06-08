# General utlities

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import pics
import colors

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

class ServePage:

    def __init__(self,rh):
        self.rh = rh
        
        #Defualts
        self.color = "indigo"
        self.nav = True
        self.admin = '<li><a href="/admin">admin</a></li>'
        self.header = ""
        self.title = "s-kape"
        self.description = "An s-kape page"
        self.img = ""
        self.url = "www.s-kape.com"
        
   
    #Sets color theme of page to load
    def setColor(self,color):
        self.color = color;
   
    #Turns off navbar
    def navOff(self):
        self.nav = False
   
    #Turns on navbar
    def navOn(self):
        self.nav = True
    
    #Creates a header
    def setHeader(self, title, subheadings, pic):
    
        #Find the picture (if there is one)
        
        picURL = ""
        
        if(pic!=""):
            p = pics.Pic.get_by_id(pic)
            #foundIt
            if (p != None):
                picURL = p.lowQualityURL
            
        color = colors.Color.get_by_id(self.color)
        
        if(color != None):
            colorOverlay = color.transparent("0.3")
            backgroundColor = color.lightest;
        else:
            colorOverlay = "rgba(0, 0, 0, 0.7)"
            backgroundColor = "white"
        
        #Load header values
        TemplateValues = {
            'title': title,
            'picURL': picURL,
            'colorOverlay': colorOverlay,
            'subheadings': subheadings,
            'backgroundColor': backgroundColor,
        }
        
        #Load header template
        template = JINJA_ENVIRONMENT.get_template('/html/header.html')
        
        self.header = template.render(TemplateValues)
        
    #Sends page back to user.
    def write(self, title, pageContent):
    
        #If the nav option is enabled, send a navbar to the user
        if (self.nav):
            
            #Make sure the main body is of the right type
            
            #The body with nave option is only needed if there is no header
            
            if(self.header == ""):
                bodyType = "body-with-nav"
            else:
                bodyType = "body"
            
            #if the current user is an admin. Enable the admin items on the bar
            user = users.get_current_user()
            
            #If the user is admin, use whatever is set for the admin control
            #Use nothing if not
            adminControl = ""
            if users.is_current_user_admin():
                adminControl = self.admin
            
            #Setup navigation template varibles
            navTemplateValues = {
                'title': title,
                'admin': adminControl,
            }
            
            #Load navigation template
            navTemplate = JINJA_ENVIRONMENT.get_template('/html/nav.html')
            
            #Create navigation bar using template
            nav = navTemplate.render(navTemplateValues)
           
        #No bar
        else:
            bodyType = "body"
            nav = ""
        
        #Setup page template variables
        pageTemplateValues = {
            'nav': nav,
            'bodyType': bodyType,
            'color': self.color,
            'pageContent': pageContent,
            'header': self.header,
            'title': self.title,
            'description': self.description,
            'img': self.img,
            'url': self.url
        }
        
        #Load page template
        pageTemplate = JINJA_ENVIRONMENT.get_template('/html/template.html')
        
        #Create page using template and serve
        self.rh.response.write(pageTemplate.render(pageTemplateValues))
        
#Tokenizes a word (used for searching autocomplets)
def tokenize_word(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                a.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
            
    return str(','.join(a))
    
    

    
   