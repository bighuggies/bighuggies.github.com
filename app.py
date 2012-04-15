import os
import json
import time
import re

from unidecode import unidecode
from datetime import datetime

import pymongo

from pymongo import Connection

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.auth


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
        if not user_json: return None
        
        user = json.loads(user_json)
        return user['name']

        
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    
class MainHandler(BaseHandler):        
    def get(self):
        self.render('index.html', posts=self.db.posts.find().sort('timestamp', direction=pymongo.DESCENDING))


class PostHandler(BaseHandler):
    def get(self, year, month, slug):
        self.render('post.html', post=self.db.posts.find_one({'slug': slug}))


class ComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('compose.html')
    
    @tornado.web.authenticated
    def post(self):
        now = datetime.now()
        
        post = {
            'title': self.get_argument('post_title'),
            'slug': slugify(self.get_argument('post_title')),
            'timestamp': datetime.utcnow(),
            'year': now.strftime("%Y"),
            'month': now.strftime("%m"),
            'day': now.strftime("%d"),
            'time': now.strftime("%H"),
            'author': self.user,
            'text': self.get_argument('post_contents')
        }
        
        self.db.posts.save(post)
        
        self.redirect('/')
        
        
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
#            (r'/post/([^/]+)', PostHandler),
            (r'/post/([0-9]{4})/([0-9]{2})/([a-zA-Z0-9-]+)', PostHandler),
            (r'/compose', ComposeHandler),
            (r"/login", AuthLoginHandler),
            (r"/logout", AuthLogoutHandler),
        ]
        settings = dict(
            environment=os.getenv('ENVIRONMENT', 'development'),
            mongodb_uri=os.getenv('MONGOHQ_URL', ''),
            db_name='app3750415',
            email='andrew@atshughson.me',
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Post": PostModule, "Jumbotron": JumbotronModule,},
            xsrf_cookies=True,
            cookie_secret="dec98554f55ca8b216be35c40dd4c29b6fe3cc5d",
            login_url="/login",
            autoescape=None,
        )
        
        tornado.web.Application.__init__(self, handlers, **settings)
        
        self.db = self.get_database()
        
        
    def get_database(self):
#        try:
        if self.settings['environment'] == 'heroku':
            connection = Connection(config['mongodb_uri'])
        else:
            connection = Connection()

        database = connection[self.settings['db_name']]
#        except:
#            print('Unable to connect to the database.')
#            return None
#    
        return database;


def main():
#    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
