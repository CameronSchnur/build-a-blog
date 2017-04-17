import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def render_front(self, title='', body='', error=''):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("front.html", title=title, body=body, error=error, posts=posts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Post(title = title, body = body)
            a.put()

            self.redirect("/blog/{0}".format(a.key().id()))
        else:
            error = "we need both a title and a post!"
            self.render_front(title, body, error)

class Blog(Handler):
    def render_post(self, title='', body='', error=''):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, body=body, error=error, posts=posts)

    def get(self):
        self.render_post()

class NewPost(Handler):
    def render_newpost(self, title='', body='', error=''):
        self.render("front.html", title=title, body=body, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Post(title = title, body = body)
            a.put()

            self.redirect("/blog/{0}".format(a.key().id()))
        else:
            error = "we need both a title and a post!"
            self.render_newpost(title, body, error)

class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        post = Post.get_by_id(id)
        self.render("post.html", body=post)

app = webapp2.WSGIApplication([('/', MainPage),
('/blog', Blog), ('/blog/newpost', NewPost), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
