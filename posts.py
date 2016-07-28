"""Posts are a main data type
    - They are stored and retrieved using nbd
    - They are added to the search index for easy Lookup

    Code in this file is for:
    - Serving posts
    - Storing posts
    - Retreiving parts of a post
"""
####################################################
#Imports and setup
####################################################

#python libs
import webapp2
import os
import markdown
from datetime import datetime
from urlparse import urlparse
import urllib2
import BeautifulSoup
import re
import jinja2

#google apis
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import app_identity
import cloudstorage as gcs

#skape libaries
import utils
import pics
import colors
import cards

#Set envronment for jinja templates
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

####################################################
#Classes
####################################################

#The storage object
class Post(ndb.Model):
    """ Contains data for posts. A post is a blog post in the blog.
        Is inheireted from ndb.model
        Additional methods for storing and retrieving posts.
    """

    #Post properties
    name = ndb.StringProperty()             #name of the post. also serves as key
    title = ndb.StringProperty()            #title of post
    date = ndb.DateProperty()               #date of post
    dateString = ndb.StringProperty()       #date of post, displayed as a string
    pic = ndb.StringProperty()              #cover pic of post. Is a reference to Pic is name pic
    color = ndb.StringProperty()            #color of post. Is a reference to Color is name color
    location = ndb.StringProperty()         #location of post
    activity = ndb.StringProperty()         #activity of post
    tags = ndb.StringProperty()             #tags of a post (comma seperated)
    relatedPosts = ndb.StringProperty()     #related posts (comma seperated)
    comment = ndb.StringProperty()          #post comment
    content = ndb.TextProperty()            #content of post. this will be in markdown
    htmlContent = ndb.TextProperty()        #content of post in HTML
    html = ndb.TextProperty()               #html of entire post (includes pics and header)
    text = ndb.TextProperty()               #text version of post
    publish = ndb.BooleanProperty()         #Whether or not the post is published
    hideHeader = ndb.BooleanProperty()      #Whether or not to display a header
    hideTitle = ndb.BooleanProperty()       #Whether or not to display a title
    hideFooter = ndb.BooleanProperty()      #Whether or not to display a footer
    hideRelated = ndb.BooleanProperty()     #Whether or not to display a related cards

    def toTxt(self):
        """ Converts a post into raw text for backup purposes"""

        #Get post elements and put them in a string
        text = "// This is a template for a blog post on s-kape.com\n\n"
        text = text + "name: " + self.name + "\n"
        text = text + "date: " + self.date.strftime("%Y-%m-%d") + "\n"
        text = text + "pic: " + self.pic + "\n"
        text = text + "color: " + self.color + "\n"
        text = text + "location: " + self.location + "\n"
        text = text + "activity: " + self.activity + "\n"
        text = text + "activity: " + self.tags + "\n"
        text = text + "comment: " + self.comment + "\n\n"
        text = text + "//Everything after the title will be included as markdown and converved into html.\n"
        text = text + "//To insert an image use the format {pic <pic-name>}\n"
        text = text + "title: " + self.title + "\n\n"

        text = text + self.content

        #Store text in nbd
        self.text = text
        self.put()

    # Renders a post.
    # Adds some dynamic content to any post
    def render(self):

        html = self.html

        #a single pic can be included in the post.
        #the format is {pic <pic name>}
        #use regex to find matches and replace them with the proper html
        html = re.sub(ur'{pic\s([A-Za-z0-9\-]*)}',_imgHTML,html)

        #pics can be included in the post.
        #the format is {pic <pics name>}
        #use regex to find matches and replace them with the proper html
        html = re.sub(ur'{pics\s([A-Za-z0-9\-\,]*)}',_imgsHTML,html)

        #cards can be included in the post.
        #the format is {cards <card name>}
        #use regex to find matches and replace them with the proper html
        html = re.sub(ur'{cards\s([A-Za-z0-9\-\:\,\s]*)}',_cardHTML,html)

        html = re.sub(ur'{cards-grey\s([A-Za-z0-9\-\:\,\s]*)}',_cardHTMLGrey,html)

        #emded html from another site
        html = re.sub(ur'{embed\s([A-Za-z0-9\-\/\.\:\%]*)}',_embedHTML,html)


        return html


    #Generates a and returns card for a post
    def genCard(self,size):
        """ Generates a and returns card for a post

            Keyword arguments:
            size -- The size of the picture to use for a post as a text string
        """

        #Check if the post has a color set. If not set to blue
        if(self.color != ""):
            color = colors.Color.get_by_id(self.color)
        else:
            color = colors.Color.get_by_id("blue")

        #Get url for the picture on the card
        picURL = pics.getPicURL(self.pic,size)

        #Get the template
        cardTemplate = JINJA_ENVIRONMENT.get_template('/html/card.html')

        #Setup template values
        cardTemplateValues = {
                'name': "post-"+self.name,
                'title': self.title,
                'url': 'href = "/posts/' + self.name + '""',
                'admin': "",
                'colorOverlay': "rgba(0, 0, 0, 0.1)",
                'colorOverlayDark': "rgba(0, 0, 0, 0.5)",
                'color': color.base,
                'picURL': picURL,
                'backgroundColor': "white",
                'backgroundColorDark': "#DDD",
                'info': self.comment,
        }

        #Render template and return
        return cardTemplate.render(cardTemplateValues)

####################################################
#Get Handlers
####################################################

#Handler for viewing a post.
#Name of the post comes from the url used
class View(webapp2.RequestHandler):
    def get(self):

        #Parse url to find name
        #url will be /posts/<post name>
        url = urlparse(self.request.url)
        name = url.path.replace("/posts/","")

        #Get the post
        p = Post.get_by_id(name)

        #Post is not found. Return error msg and exit
        if (p == None):
            page = utils.ServePage(self)
            page.write("Error","Page not found")
            return

        #Get a blank page to serve
        page = utils.ServePage(self)

        #Set the color of the page
        if(p.color != ""):
            page.setColor(p.color)

        #Add special admin options (will only be shown to admin)
        page.admin = '<li><a href="/admin/posts/' + p.name + '">edit</a></li>'

        #Set metatag data
        page.title = "s-kape | " + p.title
        page.description = p.comment
        page.img = pics.getPicURL(p.pic,"normal")
        page.url = "www.s-kape.com/posts/" + p.name
        page.pageType = "post"

        #Create the header
        #Make the sub headings
        subheadings = '<div class="ftSmall">' + p.dateString + ' / ' + p.location + ' / ' + p.activity + '</div>'

        #Set up the header (if we want a header)

        if(not p.hideHeader):
            page.setHeader(p.title,subheadings,p.pic)

        #Write the content of the post to the page

        pageHtml = p.render()

        if(not p.hideRelated and p.relatedPosts != None and p.relatedPosts != ""):

            relatedPostsArray = p.relatedPosts.split(',')
            pageHtml += cards.getCardCollection(relatedPostsArray,cardType='post',heading='Related Posts',greyBack=True)

        page.write(p.title,pageHtml)

#Dislpays plain text of post
class Text(webapp2.RequestHandler):
    def get(self):

        #Parse url to find name
        #url will be /posts/<post name>.txt
        url = urlparse(self.request.url)
        name = url.path.replace("/posts/","")
        name = name.replace(".txt","")

        #Get the post
        p = Post.get_by_id(name)

        #Set the response header to plain text
        self.response.headers['Content-Type'] = 'text/plain'

        #Write the response (Error message if not found)
        if (p == None):
            self.response.write('Page not found')

        else:
            self.response.write(p.text)

#Displays a list of posts (as cards)
#Page is ajax, so this will only send the type of query (post) that
#the page should make.
class PostList(webapp2.RequestHandler):
    def get(self):

        #Check if the url is valid. If not print an error message
        url = urlparse(self.request.url)

        if(url.path != "/posts"  and url.path != "/posts/"):

            errorPage = utils.ServePage(self)

            errorPage.title = "s-kape | post not found"
            errorPage.description = "s-kape.com post not found"
            errorPage.setColor("red")
            errorPage.img = ""
            errorPage.pageType = "post"

            errorPage.write("Posts","Post not found " + url.path)
            return

        #Get the template file
        template = JINJA_ENVIRONMENT.get_template('html/cards.html')

        #If there is a ? after then url, then do a query (/posts?<query>)
        query = ""

        if  url.query != None or url.query != "":
            query = url.query

        #Complete the template. Fill in the query type
        templateValues = {
            'queryType': "post",
            'defualtQuery': query,
        }

        #Render template
        pageHTML = template.render(templateValues)

        #Create page to display posts
        page = utils.ServePage(self)

        #Set the color of the page
        page.setColor("indigo")

        #Add special admin options (will only be shown to admin)
        page.admin = '<li><a href="/admin/post-add">add</a></li>' \
                     '<li><a href="/admin">admin</a></li>'

        #Set metatag data
        page.title = "s-kape | posts"
        page.description = "s-kape.com posts"
        page.img = ""
        page.url = "www.s-kape.com/posts"
        page.pageType = "post"
        page.search = True

        #Send page
        page.write("Posts",pageHTML)

#Sends a form that can be used to add a new post
class AddForm(webapp2.RequestHandler):
    def get(self):

        #Setup navigation template varibles
        p = Post (
            name = "new-post",
            title = "",
            date = datetime.strptime("2016-01-01", "%Y-%m-%d"),
            dateString = "2016-01-01",
            pic = "",
            color = "",
            location = "",
            activity = "",
            comment = "",
            content = "",
            relatedPosts = "",
            publish = False
        )

        #Use post values to set up template
        templateValues = {
            'post': p,
            'hideHeader': '',
            'hideTitle': '',
        }

        #Load navigation template
        template = JINJA_ENVIRONMENT.get_template('/html/post-edit.html')

        #Create navigation bar using template
        content = template.render(templateValues)

        #Create page to add a post
        page = utils.ServePage(self)

        #Set color
        page.setColor("grey")

        page.pageType = "post"

        #Set admin options
        page.admin = '<li><a class="nav-link" id="post-submit" >save</a></li>'\
                     '<li><a class="nav-link" id="info-toggle">hide</a></li>'

        #Send page
        page.write("new-post",content)

#Send form to update a post. Form will be filled in with values from post that
#is going to be edited.
class UpdateForm(webapp2.RequestHandler):
    def get(self):

        #Parse url to find name
        #url will be /admin/posts/<post name>
        url = urlparse(self.request.url)
        name = url.path.replace("/admin/posts/","")

        #Find the post
        p = Post.get_by_id(name)

        #If the page is not found, return error message and leave
        if (p == None):
            page = utils.ServePage(self)
            page.write("Error","Page not found")
            return

        #Set up wether the header, title and footer hide tick boxes
        #should be ticked

        hideHeader = ''
        if(p.hideHeader):
            hideHeader = 'checked'

        hideTitle = ''
        if(p.hideTitle):
            hideTitle = 'checked'

        hideFooter = ''
        if(p.hideFooter):
            hideFooter = 'checked'

        hideRelated = ''
        if(p.hideRelated):
            hideRelated = 'checked'

        #Setup navigation template varibles
        templateValues = {
            'post': p,
            'hideHeader': hideHeader,
            'hideTitle': hideTitle,
            'hideFooter': hideFooter,
            'hideRelated': hideRelated
        }

        #Load navigation template
        template = JINJA_ENVIRONMENT.get_template('/html/post-edit.html')

        #Create navigation bar using template
        content = template.render(templateValues)

        #Create page to modify a post
        page = utils.ServePage(self)

        #Set color to post color
        page.setColor(p.color)

        #Display whether or not post is published
        if(p.publish):
            publishText = "un-publish"
        else:
            publishText = "publish"

        #Set up admin options in nav bar
        page.admin = '<li><a class="nav-link" id="post-submit" >save</a></li>'\
                        '<li><a class="nav-link" id="post-publish">'+publishText+'</a></li>'\
                        '<li><a class="nav-link" id="info-toggle">hide</a></li>'

        page.pageType = "post"

        #Send page to edit post to user
        page.write(p.title,content)

#Re-index the search index for posts
class ReIndex(webapp2.RequestHandler):
    def get(self):

        #get the search index
        index = search.Index('posts')

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

        #Get all the posts
        allPosts = Post.query()

        #You can only put 200 at a time. So every 200 put the list and clear
        i = 0
        documents = []
        for post in allPosts:
            documents.append(makeSearchDocumet(post))
            if(i>=199):
                results = index.put(documents)
                documents = []
                i = 0
            else:
                i = i+1

        #Add the remaining docs
        results = index.put(documents)

        #Send msg
        self.response.out.write('posts re-indexed')

####################################################
#Post Handlers
####################################################

#Updates a post from post from user
class Update(webapp2.RequestHandler):
    def post(self):

        # Get the stuff from the form
        name = self.request.get('name').strip()
        title = self.request.get('title').strip()
        dateString = self.request.get('date').strip()
        pic = self.request.get('pic').strip()
        color = self.request.get('color').strip()
        location = self.request.get('location').strip()
        activity = self.request.get('activity').strip()
        tags = str.replace(str(self.request.get('tags').strip()), " ", "")
        relatedPosts = str.replace(str(self.request.get('relatedPosts').strip()), " ", "")
        comment = self.request.get('comment').strip()
        content = self.request.get('content').strip()
        add = self.request.get('add').strip()
        hideHeaderString = self.request.get('hideHeader').strip()
        hideTitleString = self.request.get('hideTitle').strip()
        hideFooterString = self.request.get('hideFooter').strip()
        hideRelatedString = self.request.get('hideRelated').strip()

        #first check if the name is valid
        regex = re.compile(ur'^[A-Za-z0-9\-]+$')

        #Not valid. Tell the user
        if (not re.match(regex, name)):
            self.response.out.write("Name can contain: 'a-z', 'A-Z', '0-9' and '-' only.")
            return

        #check if the title is valid. The length should be 20 chars max and not blank
        if(len(title) < 1):
            self.response.out.write("Title cannot be blank")
            return

        if(len(title) > 40):
            self.response.out.write("Title is too long. 40 chars max.")
            return

        #If the hideHeader from the form is true, then set the hideHeader to
        #bool True
        hideHeader = False
        if(hideHeaderString == 'true'):
            hideHeader = True

        #If the hideTitle from the form is true, then set the hideTitle to
        #bool True
        hideTitle = False
        if(hideTitleString == 'true'):
            hideTitle = True

        #If the hideFooter from the form is true, then set the hideFooter to
        #bool True
        hideFooter = False
        if(hideFooterString == 'true'):
            hideFooter = True

        #If the hideFooter from the form is true, then set the hideFooter to
        #bool True
        hideRelated = False
        if(hideRelatedString == 'true'):
            hideRelated = True

        #Check if this is an addtion or modification.
        #add will be 'yes' if it is an addition
        if(add=="yes"):
            # the title. Make sure it does not already exist
            p = Post.get_by_id(name)

            #Oh no. This already exists
            #Send the message and bail
            if(p != None):
                self.response.out.write(name + " already exists")
                return

        #Check if the date is in the correct format. If it is not tell the user and exit
        if (dateString == ""):
            date = datetime.strptime("2016-01-01", "%Y-%m-%d")
        else:
            try:
                date = datetime.strptime(dateString, "%Y-%m-%d")

            except ValueError:
                self.response.out.write("Date format is YYYY-MM-DD")
                return

        #Parse HTML from mardown
        html = markdown.markdown(content)

        #Set the publish varible. If we are adding the publish will be no.
        #If we are updating it will be whatever it used to be
        #Don't bother checking if the post exists becuase if we get this far it does
        publish = False
        p = Post.get_by_id(name)
        if(p != None):
            publish = p.publish

        #Update the post object
        updatePost = Post( name = name,
                           id = name,
                           title = title,
                           date = date,
                           dateString = dateString,
                           pic = pic,
                           color = color,
                           location = location,
                           activity = activity,
                           tags = tags,
                           relatedPosts = relatedPosts,
                           comment = comment,
                           content = content,
                           htmlContent = html,
                           publish = publish,
                           hideHeader = hideHeader,
                           hideTitle = hideTitle,
                           hideFooter = hideFooter,
                           hideRelated = hideRelated,)

        #set template values with post to be updated

        title = ""

        if(not updatePost.hideTitle):
            title = '<h1>' + updatePost.title  + '</h1>'

        #Set the tag values. Each will be links with # before them
        tagString = ""
        if updatePost.tags != "":
            tagArray = updatePost.tags.split(",")

            tagLinks = []
            for tag in tagArray:
                tagLinks.append('<a href="/posts?tags=' + tag + '">#' + tag + '</a>')

            tagString =  " ".join(tagLinks)

        #Code for hiding the footer using embedded style
        hideFooterStyle = ""

        if updatePost.hideFooter:
            hideFooterStyle = 'display: none'

        templateValues = {
            'title':  title,
            'htmlContent': updatePost.htmlContent,
            'tags': tagString,
            'hideFooterStyle': hideFooterStyle
        }

        #get the template file
        template = JINJA_ENVIRONMENT.get_template('/html/post.html')

        #render the template into the html field
        updatePost.html = template.render(templateValues)

        #put into the datastore
        updatePost.put()

        #convert post to txt and save
        updatePost.toTxt()

        #add post to search index
        addToSearch(updatePost)

        #If adding, take user to new page.
        #If updating, stay on the updating page and give the user a msg
        if (add=="yes"):
            self.response.out.write('success')
        else:
            self.response.out.write('<a href="/posts/'+name+'" >View</a> <a href="/posts/'+name+'.txt" download>Download</a>')

#####################################################################
#Ajax
#####################################################################

#post from user will toggle if the post is published or not
class PostPublish(webapp2.RequestHandler):
    def post(self):

        # Get the stuff from the form
        name = self.request.get('name').strip()

        # Get the post
        p = Post.get_by_id(name)

        # Check if post is found
        if(p == None):
            self.response.out.write("error publishing/unpublishing")
            return

        # If the post is published, then unpublish
        if(p.publish):
            p.publish = False
            msgString = "un-published"

        # If the post is un-published, then publish
        else:
            p.publish = True
            msgString = "published"

        # Update the record in the nbd
        p.put()

        # Update the search record
        addToSearch(p)

        # Send message to user
        self.response.out.write(msgString)


#####################################################################
#Public Functions
#####################################################################

def PostCard(name,size):
    """ Creates an HTML card for a post or a blank string if post
        is not found.

    Keyword arguments:
        name -- The name of the card to be found
        size -- The size (as a string) of the card to be found.
    """

    #If name is blank, return blank string
    if(name==""):
        return ""

    #Find the Post
    p = Post.get_by_id(name)

    #If post is not found, return blank string
    if (p == None):
        return ""

    return p.genCard(size)

def addToSearch(post):
    """ Add a or update a post in the search index

    Keyword arguments:
        post -- The name of the card to be found
    """

    document = makeSearchDocumet(post)
    index = search.Index('posts')
    index.delete(post.name)
    index.put(document)

def makeSearchDocumet(post):
    """ Create a search document for search index from a post

    Keyword arguments:
        post -- The name of the card to be found
    """

    #We are going to add publish the search options
    if(post.publish):
        published = "yes"
    else:
        published = "no"

    #set up the document
    document = search.Document(

        # Setting the doc_id is optional. If omitted, the search service will
        # create an identifier.
        doc_id=post.name,
        fields=[
            search.TextField(name='name', value=post.name),
            search.TextField(name='tName', value=utils.tokenize_word(post.name)),
            search.TextField(name='title', value=post.title),
            search.TextField(name='tTitle', value=utils.tokenize_word(post.title)),
            search.TextField(name='location', value=post.location),
            search.TextField(name='tLocation', value=utils.tokenize_word(post.location)),
            search.TextField(name='activity', value=post.activity),
            search.TextField(name='TActivity', value=utils.tokenize_word(post.activity)),
            search.TextField(name='tags', value=post.tags),
            search.TextField(name='comment', value=post.comment),
            search.AtomField(name='published', value=published),
            search.HtmlField(name='content', value=post.htmlContent),
            search.DateField(name='date', value=post.date)
        ])

    return document

def findCards(query):
    """Find posts in earch index using search query.

    Keyword arguments:
        query -- The query used to find posts.
                 A blank query will find all posts.
                 If the user is not an admin, they will only see un-published posts.

    Returns:
        List of posts in a string. The format is post:<post_name_1>,post:<post_name_2>,post:<post_name_n>...
        If no posts are found, a blank string is returned
    """

    postList = ""
    index = search.Index('posts')

    #Check to see if user is an administrator. If they are not, add options to query to only
    #find unpublished posts.
    user = users.get_current_user()
    if users.is_current_user_admin():
        query_string = "published: no OR published: yes " + query
    else:
        query_string = "published: yes " + query

    #Blank query, find all posts. Sort by date.
    if(query == ""):

        #Set up search to sort by date
        sort_date= search.SortExpression(
            expression='date',
            direction=search.SortExpression.DESCENDING,
            default_value=0)
        sort_options = search.SortOptions(expressions=[sort_date])
        query_options = search.QueryOptions(
            limit=1000,
            sort_options=sort_options)

        #Create query string
        query_string = search.Query(query_string=query_string, options=query_options)

    #Find posts according to search index
    documents = index.search(query_string)

    #Create comma seperated list of posts in the format post:<post_name_1>,post:<post_name_2>,post:<post_name_n>...
    posts = []
    for document in documents:
        posts.append("post:" + document.field('name').value)

    postList = ",".join(posts)

    return postList

#####################################################################
#Private Functions
#####################################################################

# Function used as parse out the image name as part of a regex
# The match will contain the name of an image.If the image exists
# then return html for a picture in a post
def _imgHTML(match):

    #See if picture exists
    name = str(match.group(1))
    p = pics.getPic(name)

    if(p==None):
        return "not found-" + name + "-"

    template = JINJA_ENVIRONMENT.get_template('/html/post-pic.html')
    templateValues = {
            'p': p,
        }

    return template.render(templateValues)

# Function used as parse out the image names as part of a regex
# The match will contain a list of name of images .If the images exists
# then return html for a picture in a post
def _imgsHTML(match):

    names = str(match.group(1))

    picCollection = []

    picCollection = names.split(",")

    #1 or 0 pics to load
    if(len(picCollection) < 1):
        picCollection.append(names)

    returnString = '<div class="grey-background">'

    picNumber = len(picCollection)

    colDiv = '<div class="col-sm-12">'

    if(picNumber == 2):
        colDiv = '<div class="col-sm-6">'
    if(picNumber == 3):
        colDiv = '<div class="col-sm-4">'
    if(picNumber == 4):
        colDiv = '<div class="col-sm-6">'
    if(picNumber > 4):
        colDiv = '<div class="col-sm-4">'

    for pic in picCollection:

        if(pic != ""):
            p = pics.getPic(pic)

            if (p != None):

                template = JINJA_ENVIRONMENT.get_template('/html/post-pic.html')
                templateValues = {
                    'p': p,
                }

                picHtml = template.render(templateValues)

                returnString = returnString + colDiv + picHtml + "</div>"

    return returnString + "</div>"


    if(p==None):
        return "not found-" + name + "-"

    template = JINJA_ENVIRONMENT.get_template('/html/post-pic.html')
    templateValues = {
            'p': p,
        }

    return template.render(templateValues)


# Function used as parse out card names and return the cards (html)
# The card name will be in the format <type>:<name> and seperated by columns.
# The are some special keywords that will perform a special function instead
def _cardHTML(match):

    #See if cards exists
    cardsString = str(match.group(1))
    return _cardHTMLChooseBack(cardsString,False)

def _cardHTMLGrey(match):

    #See if cards exists
    cardsString = str(match.group(1))
    return _cardHTMLChooseBack(cardsString,True)



def _cardHTMLChooseBack(cardsString,greyBack):

    title = ""
    cardCollection = []
    # latest-posts is a special keyword that will return post cards in order of date
    if (cardsString == "latest-posts"):

        #The blank query to findCards will order the posts automatically
        cardCollection = findCards("").split(",")
        title = "Lastest Posts"

    # latest-pics is a special keyword that will return pic cards in order of date
    elif (cardsString == "latest-pics"):

        #The blank query to findCards will order the pics automatically
        cardCollection = pics.findCards("").split(",")
        title = "Lastest Pics"

    elif (',' in cardsString):

        cardsStringArray = cardsString.split(",")
        title = cardsStringArray[0]
        cardCollection = cardsStringArray[1:]

    if greyBack:
        return cards.getCardCollection(cardCollection,heading=title,greyBack=True)
    else:
        return cards.getCardCollection(cardCollection,heading=title)


def _embedHTML(match):



    url = str(match.group(1))

    page = urllib2.urlopen(url).read()

    soup = BeautifulSoup.BeautifulSoup(page)
    txt = str(soup.find('body'))

    #gcs_file = gcs.open(url)


    #return gcs_file.read()

    return txt
