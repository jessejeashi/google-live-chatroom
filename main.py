import webapp2
import os
import jinja2
import logging
from datetime import datetime
from datetime import timedelta

from google.appengine.api import users, channel
from google.appengine.ext import db, ndb

from django.utils import simplejson as json

ROOT_PATH = os.path.dirname(__file__)
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.join(ROOT_PATH, 'templates')),extensions=['jinja2.ext.autoescape'],autoescape=True)
logging.getLogger().setLevel(logging.DEBUG)


class Channels(db.Model):
    channel_id  = db.StringProperty(default = "")
    
class Form(ndb.Model):
    name = ndb.StringProperty()  

class Rec(ndb.Model):
    content = ndb.StringProperty()
    imageId = ndb.IntegerProperty()
    date=ndb.DateTimeProperty(auto_now_add=True)

class DatastoreFile(ndb.Model):
    data = ndb.BlobProperty(default=None)  # max size  < 1mb
    mimetype = ndb.StringProperty(required=True) 
    userId = ndb.IntegerProperty()  

class Chat(ndb.Model):
    chat_name = ndb.StringProperty()
    owner = ndb.StringProperty()
    url=ndb.StringProperty()
    description=ndb.StringProperty()
    userId = ndb.IntegerProperty() 
    imageId=ndb.IntegerProperty()
    status=ndb.IntegerProperty()
    clicks=ndb.IntegerProperty()
    date=ndb.DateTimeProperty(auto_now_add=True)

class IndexPage(webapp2.RequestHandler):
    def get(self):
            q=ndb.gql("SELECT * from Chat ORDER BY date DESC")
            items=q.get()
            items=q.fetch()

            all_channels    = Channels.all().fetch(1000)
            count = len(all_channels)

            template_values = {
            'items':items,
            'count':count
            }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))

class Index2Page(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        if user:
            q=ndb.gql("SELECT * from Chat ORDER BY date DESC")
            items=q.get()
            items=q.fetch()

            all_channels    = Channels.all().fetch(1000)
            count = len(all_channels)
            name = user.nickname()


            template_values = {
            'nickname':name,
            'items':items,
            'count':count
            }
            template = jinja_environment.get_template('index2.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class PersonalHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url('/')
    if user:
    	    m=int(user.user_id()[0:15])
    	    p=ndb.gql("SELECT * from Chat where userId=%d and status!=1" %(m))
    	    playings=p.get()
    	    playings=p.fetch()
            all_channels    = Channels.all().fetch(1000)
            count = len(all_channels)
            name = user.nickname()
            template_values = {
            'nickname'  : user.nickname(),
            'playings'   : playings,
            'email': user.email(),
            'logout_url': logout_url,
            'count':count
            }
            template = jinja_environment.get_template('personal_page.html')
            self.response.out.write(template.render(template_values))
    else:
        self.redirect(users.create_login_url(self.request.uri))

  def post(self):
    user = users.get_current_user()

    a=self.request.get("closed")
    if(a):
    	    p=ndb.gql("SELECT * from Chat where imageId=%d" %(int(a)))
    	    playings=p.get()
    	    playings=p.fetch()[0]
    	    playings.status=1
    	    playings.put()
            self.redirect('/personal_page')

    else:
            chat_name = self.request.get('chat_name')
            owner = self.request.get('owner')
            url = self.request.get('url')
            description = self.request.get('description')
            file = self.request.POST['file']
            m=int(user.user_id()[0:15])
            entity = DatastoreFile(userId=m, data=file.value, mimetype=file.type)
            entity.put()
            chat = Chat(userId=m,chat_name=chat_name, owner=owner,url=url,clicks=1,description=description,imageId=entity.key.id())
            chat.put()

            file_url = "http://%s/file/download/%d" % (self.request.host, entity.key.id())
            chat_url = "http://%s/chat_page/%d" % (self.request.host, entity.key.id())
            self.redirect('/personal_page')

class DownloadHandler(webapp2.RequestHandler):
  def get(self, id):
        # can use get_by_id if you know the number id of the entity
    entity = DatastoreFile.get_by_id(int(id))
    self.response.headers['Content-Type'] = str(entity.mimetype)
    self.response.out.write(entity.data)   



                     
         
class PostMsg(webapp2.RequestHandler):

    def post(self):
        user            = users.get_current_user()
        message1 = "%s" % (self.request.get('message'))
        if "[Recommend]" in str(message1):
            message = "<h4>%s : %s </h4></br><h1>%s</h1><div><a class='changeToA' onclick='onClickMehthod(%s,%s,%s);'>Watch this</a ></div></br>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),(datetime.now()+timedelta(hours=8)).strftime('%H'),(datetime.now()+timedelta(hours=8)).strftime('%M'),(datetime.now()+timedelta(hours=8)).strftime('%S'))
            content = message
            channel_id = user.user_id()[0:15]
            form = Rec(key=ndb.Key('Rec',content),content=content)
            form.put()
        else:
            message = "<h4>%s : %s </h4></br><h1>%s</h1>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))


        # message = "<h4>%s : %s </h4></br><h1>%s</h1><input type = 'text' id = 'send_time' name='send_time' value='%s' size = '1' /></br>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),(datetime.now()+timedelta(hours=8)).strftime('%H:%M:%S'))
        all_channels    = Channels.all().fetch(1000)
        for c in all_channels:
            channel_msg = json.dumps({'success': True, 'html': message})
            logging.debug('sending message to:' + c.channel_id)
            channel.send_message(c.channel_id, channel_msg)
 

class ChatHandler(webapp2.RequestHandler):
    
    def get(self,id):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        p=ndb.gql("SELECT * from Chat where imageId=%d"%(int(id)))
        chat=p.get()
        chat=p.fetch()[0]
        chat.clicks=chat.clicks+1
        chat.put()     
        if user:
            all_channels    = Channels.all().fetch(1000)
            count = len(all_channels)
            content = ''
            q = ndb.gql("SELECT * from Rec where imageId=%d ORDER BY date ASC"%(int(id)))
            results = q.get()
            results = q.fetch()
            for entity in results:
                content=content+str(entity.content)

            channel_id = user.user_id()[0:15]
            chat_token = channel.create_channel(channel_id)
            template_values = {
            'nickname':user.nickname(),
            'chat_token': chat_token,
            'chat':chat,
            'logout_url': logout_url,
            'count':count,
            'content':content
            }
            template = jinja_environment.get_template('chat_page.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user            = users.get_current_user()
        message1 = "%s" % (self.request.get('message'))
        imageIds = "%s" % (self.request.get('imageIds'))
        if "[Recommend]" in str(message1):
            message = "<h4>%s : %s </h4></br><h1>%s</h1><div><a class='changeToA' onclick='onClickMehthod(%s,%s,%s);'>Watch this</a ></div></br>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),(datetime.now()+timedelta(hours=8)).strftime('%H'),(datetime.now()+timedelta(hours=8)).strftime('%M'),(datetime.now()+timedelta(hours=8)).strftime('%S'))
            content = message
            channel_id = user.user_id()[0:15]
            form = Rec(key=ndb.Key('Rec',content),content=content,imageId =int(imageIds))
            form.put()
        else:
            message = "<h4>%s : %s </h4></br><h1>%s</h1>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))

        # message = "<h4>%s : %s </h4></br><h1>%s</h1><input type = 'text' id = 'send_time' name='send_time' value='%s' size = '1' /></br>" % (user.nickname(), self.request.get('message'),(datetime.now()+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),(datetime.now()+timedelta(hours=8)).strftime('%H:%M:%S'))
        all_channels    = Channels.all().fetch(1000)
        for c in all_channels:
            channel_msg = json.dumps({'success': True, 'html': message})
            logging.debug('sending message to:' + c.channel_id)
            channel.send_message(c.channel_id, channel_msg)



class Disconnected(webapp2.RequestHandler):
    def post(self):
        client_id   = self.request.get('from')
        logging.debug('client_id:' + client_id + 'disconnected')
        logging.info('client_id:' + client_id + 'disconnected')
        channel_key = db.Key.from_path('Channels', client_id)
        current_channel = db.get(channel_key)
        key = ndb.Key('Form', client_id)
        form = key.get().name        
        message2        = '<h3> Beep: %s disconnected</h3></br>' % (str(form))
        all_channels    = Channels.all().fetch(1000)
        for c in all_channels:
            channel_msg = json.dumps({'success': True, 'html': message2})
            logging.debug('sending message to:' + c.channel_id)
            channel.send_message(c.channel_id, channel_msg)  
        if current_channel:
            db.delete(channel_key)
            

class Connected(webapp2.RequestHandler):
    def post(self):
        client_id   = self.request.get('from')
        logging.info('client_id:' + client_id + ' has connected</br>')
        channel_key = db.Key.from_path('Channels', client_id)
        current_channel = db.get(channel_key)
        if not current_channel:
            current_channel = Channels(key_name = client_id, channel_id = client_id)
            current_channel.put()
        key = ndb.Key('Form', client_id)
        form = key.get().name    
        message2        = '<h2> Beep: %s connected</h2></br>' % (str(form))
        #message2        = '<h2>'+  str(form)  +' connected</h2></br>'
        all_channels    = Channels.all().fetch(1000)
        for c in all_channels:
            channel_msg = json.dumps({'success': True, 'html': message2})
            logging.debug('sending message to:' + c.channel_id)
            channel.send_message(c.channel_id, channel_msg) 
            

class Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))


class PlayingHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        m=int(user.user_id()[0:15])
        #sellings=Form.query(Form.userId=m)
        p=ndb.gql("SELECT * from Chat where userId=%d and status!=1" %(m))
        playings=p.get()
        playings=p.fetch()
        template_values = {
                    'nickname'  : user.nickname(),
                    'playings'   : playings,
                    'logout_url': logout_url
        }
        template = jinja_environment.get_template('chat_playing.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        a=self.request.get("closed")
        p=ndb.gql("SELECT * from Chat where imageId=%d" %(int(a)))
        playings=p.get()
        playings=p.fetch()[0]
        playings.status=1
        playings.put()
        #self.redirect("/sold")
        
class HistoryHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        m=int(user.user_id()[0:15])
        logging.info("********************")
        logging.info(m)
        #sellings=Form.query(Form.userId=m)
        p=ndb.gql("SELECT * from Chat where userId=%d and status=1" %(m))
        logging.info("ok")
        closeds=p.get()
        closeds=p.fetch()
        template_values = {
                    'nickname'  : user.nickname(),
                    'closeds'   : closeds,
                    'logout_url': logout_url
        }
        template = jinja_environment.get_template('chat_history.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        a=self.request.get("reopen")
        p=ndb.gql("SELECT * from Chat where imageId=%d" %(int(a)))
        playings=p.get()
        playings=p.fetch()[0]
        playings.status=0
        playings.put()




app = webapp2.WSGIApplication(
        [
            webapp2.Route('/personal_page', PersonalHandler, name='personal_page'),
            ('/file/download/(\d+)', DownloadHandler),
            ('/chat_page/(\d+)',ChatHandler),
            ('/', IndexPage),
            ('/index2', Index2Page),
            ('/index',IndexPage),
            ('/post/', ChatHandler),
            ('/logout/', Logout),
            ('/chat_playing',PlayingHandler),
            ('/chat_history',HistoryHandler),
            ('/_ah/channel/disconnected/', Disconnected),
            ('/_ah/channel/connected/', Connected)
        ],
        debug = True)
