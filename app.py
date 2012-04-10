import os
import tornado.ioloop
import tornado.web
import datetime
import pymongo

from pymongo import Connection

config = {
    'dev': False,
    'mondodb_uri': os.environ.get('MONGOLAB_URI'),
    'db_name': 'atsdatabase'
    }

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
    }

#db_ref = {
#            'database': get_database()
#    }


def get_database():
    if config['dev'] == True:
        try:
            if config['dev'] == True:
                connection = Connection()
            else:
                connection = Connection(config['mongodb_uri'])

            database = connection[config['db_name']]
        except:
            print('Unable to connect to the database.')
            return None

    return database;

database = get_database()

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

