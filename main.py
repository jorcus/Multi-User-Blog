import os
import re
from model import *
from secret import *

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and USER_RE.match(username)


def valid_password(password):
    PASS_RE = re.compile(r"^.{3,20}$")
    return password and PASS_RE.match(password)


def valid_email(email):
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return not email or EMAIL_RE.match(email)


class Signup(Handler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username').strip().lower()
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(Handler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username').strip().lower()
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')


def render_post(response, post):
    response.out.write(post.subject)
    response.out.write(post.content)


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class Main(Handler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('main.html', posts=posts)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    likes = db.IntegerProperty(required=True)
    creator = db.IntegerProperty(required=True)

    @db.ComputedProperty
    def link_subject(self):
        return self.subject.replace(' ', '-')

    def render(self):
        self.render_content = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

    @property
    def comments(self):
        return Comment.all().filter("post = ", str(self.key().id()))


class PostPage(Handler):
    def get(self, id):
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))

        if not post:
            return self.render('error404.html')
        self.render("permalink.html", post=post)


class NewPost(Handler):
    def get(self):
        if self.user:
            return self.render("newpost.html")
        else:
            return self.redirect("/login")

    def post(self):
        if not self.user:
            return self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')
        creator = self.user.key().id()

        if subject and content:
            p = Post(parent=blog_key(),
                     subject=subject,
                     content=content,
                     creator=creator,
                     likes=0)
            p.put()
            return self.redirect('/%s' % str(p.key().id()))
        else:
            error = "Please insert subject and content!"
            return self.render("newpost.html",
                               subject=subject,
                               content=content,
                               error=error)


class EditPost(Handler):
    def get(self, id):
        if not self.user:
            return self.redirect("/login")
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        elif not self.user.key().id() == post.creator:
            error = 'Only post creator allowed to edit this post'
            return self.render('error.html', error=error)
        else:
            return self.render(
                'newpost.html',
                subject=post.subject,
                content=post.content,
                edit=True)

    def post(self, id):
        if not self.user:
            return self.redirect('/login')
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        elif not self.user.key().id() == post.creator:
            error = 'Only post creator edit to delete this post'
            return self.render('error.html', error=error)
        else:
            post.subject = self.request.get('subject')
            post.content = self.request.get('content')
            post.put()
            return self.redirect('/%s' % id)


class DeletePost(Handler):
    def get(self, id):
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        if not self.user:
            return self.redirect("/login")
        elif not self.user.key().id() == post.creator:
            error = 'Only post creator allowed to delete this post'
            return self.render('error.html', error=error)
        else:
            return self.render(
                'delete.html',
                id=id, subject=post.subject)

    def post(self, id):
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        if not self.user.key().id() == post.creator:
            return self.redirect('/login')
        post.delete()
        return self.render('successful_delete.html', subject=post.subject)


class LikePost(Handler):
    def get(self, id):
        if not self.user:
            return self.redirect('/login')

        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        if not self.user.key().id() == post.creator:
            error = 'Your are not allow to Like own post'
            return self.render('error.html', error=error)
        else:
            post.likes += 1
            post.put()
            return self.redirect("/%s" % id)


class NewComment(Handler):
    def get(self, id):
        if not self.user:
            return self.redirect("/login")
        post = db.get(db.Key.from_path('Post',
                                       int(id),
                                       parent=blog_key()))
        if not post:
            return self.render('error404.html')
        return self.render("comment.html",
                           subject=post.subject,
                           content=post.content,
                           postkey=post.key())

    def post(self, id):
        post = db.get(db.Key.from_path('Post',
                                       int(id),
                                       parent=blog_key()))
        if not post:
            return self.render('error404.html')
        if not self.user:
            return self.redirect('/login')
        comment = self.request.get('comment')
        if comment:
            c = Comment(creator=self.user.key().id(),
                        comment=comment,
                        post=id,
                        parent=blog_key(),
                        creator_name=self.user.name)
            c.put()
            return self.redirect('/%s' % str(id))
        else:
            error = "Comment invalid"
            return self.render("comment.html",
                               parent=self.user.key(),
                               subject=post.subject,
                               content=post.content,
                               postkey=post.key(),
                               error=error)


class UpdateComment(Handler):
    def get(self, id, comment_id):
        post = db.get(db.Key.from_path('Post', int(id), parent=blog_key()))
        if not post:
            return self.render('error404.html')
        comment = db.get(db.Key.from_path('Comment',
                                          int(comment_id),
                                          parent=blog_key()))
        if self.user.key().id() == comment.creator:
            return self.render("comment.html",
                               subject=post.subject,
                               content=post.content,
                               comment=comment.comment,
                               postkey=post.key(),
                               edit=True)
        else:
            error = 'Only comment owner can edit the comment'
            return self.render('error.html', error=error)

    def post(self, id, comment_id):
        comment = db.get(db.Key.from_path('Comment',
                                          int(comment_id),
                                          parent=blog_key()))
        if comment:
            comment.comment = self.request.get('comment')
            comment.put()
            return self.redirect('/%s' % str(id))


class DeleteComment(Handler):
    def get(self, id, comment_id):
        if not self.user:
            return self.redirect('/login')
        comment = db.get(db.Key.from_path('Comment',
                                          int(comment_id),
                                          parent=blog_key()))
        if comment and self.user.key().id() == comment.creator:
            comment.delete()
            return self.redirect('/%s' % str(id))
        else:
            error = 'Only comment owner can delete the comment'
            return self.render('error.html', error=error)


app = webapp2.WSGIApplication([('/?', Main),
                               ('/([0-9]+)', PostPage),
                               ('/newpost', NewPost),
                               ('/([0-9]+)/delete', DeletePost),
                               ('/([0-9]+)/edit', EditPost),
                               ('/([0-9]+)/likes', LikePost),
                               ('/([0-9]+)/comment', NewComment),
                               ('/([0-9]+)/deletecomment/([0-9]+)', DeleteComment),
                               ('/([0-9]+)/updatecomment/([0-9]+)', UpdateComment),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)
                               ], debug=True)
