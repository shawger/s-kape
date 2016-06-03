# main hanlder for admin functions

import webapp2
import posts
import pics
import colors
import utils

class AdminPage(webapp2.RequestHandler):
    def get(self):
        
        page = utils.ServePage(self)
        page.setColor("grey")
        
        html = '<h1>Admin</h1>' \
               '<p><a href="/admin/update-colors">Update Colors</a></p>' \
               '<p><a href="/admin/posts-reindex">Reindex Posts</a></p>' \
               '<p><a href="/admin/pics-reindex">Reindex Pics</a></p>' \
               '<p><a href="/admin/pics-bucket">Pics from bucket</a></p>'
            
        page.write("admin",html)

app = webapp2.WSGIApplication([
    ('/admin/post-add', posts.AddForm),
    ('/admin/posts/.*', posts.UpdateForm),
    ('/admin/post-update', posts.Update),
    ('/admin/post-publish', posts.PostPublish),
    ('/admin/posts-reindex', posts.ReIndex),
    ('/admin/pic-add', pics.AddForm),
    ('/admin/pics/.*', pics.UpdateForm),
    ('/admin/pic-update', pics.Update),
    ('/admin/pics-reindex', pics.ReIndex),
    ('/admin/pics-bucket', pics.PicsInBucket),
    ('/admin/pics-bucket/.*', pics.AddFromBucketForm),
    ('/admin/update-colors', colors.LoadFromFile),
    ('/admin/', AdminPage),
    ('/admin', AdminPage),
    ], debug=True)
    
