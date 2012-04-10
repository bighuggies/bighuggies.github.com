import os
import tornado.ioloop
import tornado.web
import datetime
import pymongo

from urlparse import urlparse
from pymongo import Connection

config = {
    'production': os.environ.get('ENVIRONMENT') == 'heroku',
    'mongodb_uri': os.environ.get('MONGOHQ_URL', ''),
    'db_name': 'app3750415'
    }

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
    }

def get_database():
    try:
        if config['production'] == True:
            connection = Connection(config['mongodb_uri'])
        else:
            connection = Connection()

        database = connection[config['db_name']]
    except:
        print('Unable to connect to the database.')
        return None

    return database;

database = get_database()
print database

class MainHandler(tornado.web.RequestHandler):        
    def get(self):
        self.render('templates/index.html', posts=database.posts.find())

class WritePostHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/write_post.html')
        
    def post(self):
        post = {
            'title': self.get_argument('post_title'),
            'date': 'today',
            'author': 'Andrew Hughson',
            'text': self.get_argument('post_contents')
        }
        
        database.posts.save(post)
        
        self.redirect('/')
                    
application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/write_post', WritePostHandler),
], **settings)

if __name__ == '__main__':
    application.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()

