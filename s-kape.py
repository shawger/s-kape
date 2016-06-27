# main hanlder for s-kape web page

import webapp2
import posts
import utils
import colors
import cards
import pics
import os

import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

class MainPage(webapp2.RequestHandler):
    def get(self):
        
        #Content of the main page is a special
        #post named start.
        #Find the start post and load it up
        
        p = posts.Post.get_by_id("start")
        
        #The page is not set up. Send a defualt start
        if(p== None):
            page = utils.ServePage(self)
            page.setColor("blue")
            page.setHeader("S-Kape","","ama-dabla")
            page.write("","")
            
        else:
            page = utils.ServePage(self)
            
            #Set the color of the page
            page.setColor(p.color)
            
            #Create the header
            #Make the sub headings
            page.setHeader(p.title,'<div class="ftSmall">' + p.comment +'</div>',p.pic)
            
            #Set metatag data
            page.title = "s-kape"
            page.description = "s-kape.com home page"
            page.img = pics.getPicURL(p.pic,"normal")
            page.url = "www.s-kape.com"
            
            page.write(p.title,p.html)
            
class AboutPage(webapp2.RequestHandler):
    def get(self):
        
        #Content of the main page is a special
        #post named start.
        #Find the start post and load it up
        
        p = posts.Post.get_by_id("about")
        
        #The page is not set up. Send a defualt start
        if(p== None):
            page = utils.ServePage(self)
            page.setColor("orange")
            page.pageType = "about"
            page.write("about","This is supposed to be about the s-kape page.")
            
            
        else:
            page = utils.ServePage(self)
            
            #Set the color of the page
            page.setColor(p.color)
            
            #Set metatag data
            page.title = "s-kape | about"
            page.description = "About s-kape.com"
            page.img = ""
            page.url = "www.s-kape.com/about"
            page.pageType = "about"
            
            page.write(p.title,p.html)

class ResumePage(webapp2.RequestHandler):
    def get(self):
        
        #Content of the main page is a special
        #post named start.
        #Find the start post and load it up
        
        p = posts.Post.get_by_id("resume")
        
        #The page is not set up. Send a defualt start
        if(p== None):
            page = utils.ServePage(self)
            page.setColor("blue")
            page.setHeader("Resume","","yoho")
            page.write("","This should be my resume.")
            
        else:
            page = utils.ServePage(self)
            
            #Set the color of the page
            page.setColor(p.color)
            
            #Create the header
            #Make the sub headings
            page.setHeader('Nick Shaw','<div class="ftSmall">Resume</div>',p.pic)
            
            #Set metatag data
            page.title = "Resume"
            page.description = "Nick Shaw's Resume'"
            page.img = pics.getPicURL(p.pic,"normal")
            page.url = "www.s-kape.com/resume"
            page.pageType = "about"
            
            page.write(p.title,p.html)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/about', AboutPage),
                               ('/resume', ResumePage),
                               ('/posts', posts.PostList),
                               ('/posts/', posts.PostList),
                               ('/posts/.*.txt', posts.Text),
                               ('/posts/.*', posts.View),
                               ('/pics', pics.PicList),
                               ('/pics-url', pics.PicURL),
                               ('/pics-modal', pics.PicModal),
                               ('/pics/.*', pics.View),
                               ('/colors/.*.css',colors.CSS),
                               ('/cards/search',cards.Search),
                               ('/cards/get',cards.Get)
], debug=True)