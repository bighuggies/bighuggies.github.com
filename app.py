import os
import tornado.ioloop
import tornado.web
import datetime
import pymongo

from pymongo import Connection

config = {
    'dev': True,
    'mondodb_uri': os.environ.get('MONGOLAB_URI'),
    'db_name': 'posts'
}

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


class Post(object):
    def __init__(self, title='No Title', author='Andrew Hughson', date=datetime.date.today()):
        self.title = title
        self.author = author
        self.date = date
        self.text = ''

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        
        self.render('templates/index.html')

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
    }
        
application = tornado.web.Application([
    (r'/', MainHandler),
], **settings)

if __name__ == '__main__':
    application.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()

