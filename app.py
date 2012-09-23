import os
import json
import re
from datetime import datetime

from unidecode import unidecode

import pymongo
from pymongo import Connection
import bson

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.auth

import markdown

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None

        user = json.loads(user_json)
        return user['name']

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)


class MainHandler(BaseHandler):
    def get(self):
        posts = self.db.posts.find().sort('timestamp', direction=pymongo.DESCENDING)
        bookmarks = self.db.bookmarks.find(sort=[('_id', -1)])

        self.render('index.html', posts=posts, bookmarks=bookmarks)


class PostHandler(BaseHandler):
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug})

        if post:
            self.render('post.html', post=post)
        else:
            self.send_error(status_code=404)


class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, slug):
        self.db.posts.remove({'slug': slug})

        self.redirect('/')


class ComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        slug = self.get_argument('post', None)
        self.render('compose.html', post=self.db.posts.find_one({'slug': slug}))

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('post_id', None)

        if id:
            post = {
                'title': self.get_argument('post_title'),
                'text': self.get_argument('post_contents'),
                'html': markdown.markdown(self.get_argument('post_contents'))
            }

            self.db.posts.update({'_id': bson.objectid.ObjectId(id)}, {'$set': post})
        else:
            post = {
                'title': self.get_argument('post_title'),
                'slug': slugify(self.get_argument('post_title')),
                'timestamp': datetime.utcnow(),
                'author': self.user,
                'text': self.get_argument('post_contents'),
                'html': markdown.markdown(self.get_argument('post_contents'))
            }

            self.db.posts.save(post)

        self.redirect('/')


class BookMarkHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id', None)

        if id:
            self.db.bookmarks.remove({'_id': bson.objectid.ObjectId(id)})

        self.redirect('/')

    def post(self):
        bookmark = json.loads(self.request.body)
        self.db.bookmarks.save(bookmark)

    def check_xsrf_cookie(self):
        pass


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self._on_auth)
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            self.authenticate_redirect()
            raise tornado.web.HTTPError(500, "Google auth failed")

        if user['email'] == self.application.settings['email']:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.redirect("/")
        else:
            raise tornado.web.HTTPError(500, "NO LOGIN 4 U")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")


class PostModule(tornado.web.UIModule):
    def render(self, post):
        return self.render_string("modules/post.html", post=post)


class JumbotronModule(tornado.web.UIModule):
    def render(self):
        return self.render_string("modules/jumbotron.html")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/post/([a-zA-Z0-9-]+/?)', PostHandler),
            (r'/compose', ComposeHandler),
            (r'/delete/([a-zA-Z0-9-]+/?)', DeleteHandler),
            (r'/bookmark', BookMarkHandler),
            (r"/login/?", AuthLoginHandler),
            (r"/logout/?", AuthLogoutHandler),
        ]
        settings = dict(
            environment=os.getenv('ENVIRONMENT', 'development'),
            mongodb_uri=os.getenv('MONGOHQ_URL', ''),
            email='andrew@atshughson.me',
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Post": PostModule, "Jumbotron": JumbotronModule},
            xsrf_cookies=True,
            cookie_secret="dec98554f55ca8b216be35c40dd4c29b6fe3cc5d",
            login_url="/login",
            autoescape=None,
            debug=False
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = self.get_database()

    def get_database(self):
        if self.settings['environment'] == 'heroku':
            connection = Connection(self.settings['mongodb_uri'])
            dbname = self.settings['mongodb_uri'].split('/')[-1]
        else:
            connection = Connection()
            dbname = 'test'

        database = connection[dbname]

        return database


def main():
#    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
