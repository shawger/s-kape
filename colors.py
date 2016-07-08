# Scripts for messing with the colors on the site.
# This thing is gonna be really colorful

import jinja2
import webapp2
import csv
import os
from urlparse import urlparse

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#The storage object
class Color(ndb.Model):

    name = ndb.StringProperty()
    base = ndb.StringProperty()
    lighter = ndb.StringProperty()
    lightest = ndb.StringProperty()
    darker = ndb.StringProperty()
    darkest = ndb.StringProperty()
    r = ndb.StringProperty()
    b = ndb.StringProperty()
    g = ndb.StringProperty()
    css = ndb.StringProperty()

    def transparent(self,opacity):
        return "rgba(" + self.r + "," + self.g + "," + self.b + "," + opacity + ")"

#Lets make a CSS using a requested color
class CSS(webapp2.RequestHandler):
    def get(self):

        # First lets find out what color we want from the url
        # www.blahblah.com/colors/black.css we want the black

        p = urlparse(self.request.url)
        color = p.path.replace("/colors/","")
        color = color.replace(".css","")

        #Now we go the name of the color we want
        #Time to get the map
        if (color == ""):
            colorMap = Color.get_by_id("blue")
        else:
            colorMap = Color.get_by_id(color)

        #If the lookup don't work, lets use blue!
        if (colorMap == None):
           colorMap = Color.get_by_id("blue")

        # Set up the css header. Make sure it always refreshes
        self.response.headers['Content-Type'] = 'text/css'
        self.response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Expires'] = '0'

        # Return the sheet
        self.response.write(colorMap.css)


#Loads colors from csv into the ndb
class LoadFromFile(webapp2.RequestHandler):
    def get(self):

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('writing colors to nbd\n')
        #a counter
        i = 0

        #find the path to the config file
        path = os.path.join(os.path.dirname(__file__), 'config/colors.csv')

        #parse the config file
        with open(path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)

            #go through all the records and insert them into the ndb
            for c in reader:
                self.response.write(c['color'] + "\n")
                color = Color(name = c['color'],
                              id = c['color'],
                              base = "#" +  c['base'],
                              lighter = "#" +  c['lighter'],
                              lightest = "#" +  c['lightest'],
                              darker = "#" + c['darker'],
                              darkest = "#" +  c['darkest'],
                              r = c['r'],
                              b = c['b'],
                              g = c['g'])

                #Create a css using a template

                #Setup the template varibles
                template_values = {'color': color,
                                   'transparent': color.transparent("0.07"),}

                #Use the colors.css as template
                template = JINJA_ENVIRONMENT.get_template('config/colors.css')

                #Create the .css from the template and save it
                color.css = template.render(template_values)

                #Commit the color to the nbd
                color.put()
