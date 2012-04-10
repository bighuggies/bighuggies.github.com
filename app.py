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
        
        {'title': 'Test 2', 'author': 'Andrew Hughson', 'date': '2012-04-10', 'text': 'lorem ipsum'}

class MainHandler(tornado.web.RequestHandler):
    def initialise(self, db_ref):
        self.db = db_ref
        
    def get(self):
        posts = db.posts.find().limit(3)
        self.render('templates/index.html', posts=posts)

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static')
    }

db_ref = {
            'db_ref': get_database()
}
        
application = tornado.web.Application([
    (r'/', MainHandler, db_ref),
], **settings)

if __name__ == '__main__':
    application.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.instance().start()

