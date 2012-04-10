import os
import tornado.ioloop
import tornado.web
import datetime
import pymongo

from urlparse import urlparse
from pymongo import Connection

config = {
    'production': os.environ.get('ENVIRONMENT') == 'heroku',
    'mongodb_uri': os.environ.get('MONGOHQ_URL'),
    'mongodb_user': urlparse(os.environ.get('MONGOHQ_URL')).username,
    'mongodb_pwd': urlparse(os.environ.get('MONGOHQ_URL')).password,
    'db_name': 'atsdatabase'
    }

print(config)

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
database.authenticate(config['mongodb_user'], config['mongodb_pwd'])

class MainHandler(tornado.web.RequestHandler):        
    def get(self):
        posts = database.posts.find()
        self.render('templates/index.html', posts=posts)

        
application = tornado.web.Application([
    (r'/', MainHandler),
], **settings)

if __name__ == '__main__':
    application.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()

