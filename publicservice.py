from google.appengine.api import users
from google.appengine.ext import db
from geo.geomodel import GeoModel
import bobo
import chameleon.zpt.loader

import os
import random

class Quotes(GeoModel):
    """A location-aware class for quotes.
    """
    quote = db.StringProperty()
    name = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    rand = db.FloatProperty()
    timestamp = db.DateTimeProperty(auto_now=True)

    def _get_latitude(self):
      return self.location.lat if self.location else None

    def _set_latitude(self, lat):
      if not self.location:
        self.location = db.GeoPt()

      self.location.lat = lat

    latitude = property(_get_latitude, _set_latitude)

    def _get_longitude(self):
      return self.location.lon if self.location else None

    def _set_longitude(self, lon):
      if not self.location:
        self.location = db.GeoPt()

      self.location.lon = lon

    longitude = property(_get_longitude, _set_longitude)

template_path = os.path.join(os.path.dirname(__file__), 'templates')

template_loader = chameleon.zpt.loader.TemplateLoader(
        template_path,
        auto_reload=os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'))
        
master = template_loader.load('master.html')

@bobo.query('/')
def index():
    template = template_loader.load('index.html')
    rand_num = random.random()
    randomquote = Quotes.all().order('rand').filter('rand >=', rand_num).get()
    if randomquote is None:
        randomquote = Quotes.all().order('-rand').filter('rand <', rand_num).get()
    return template(master=master, quote=randomquote)

@bobo.query('/q/:quote_id')
def quote(quote_id):
    template = template_loader.load('quote.html')
    quote = Quotes.get_by_id(int(quote_id))
    return template(master=master, quote=quote)

@bobo.query('/addform')
def addform():
    template = template_loader.load('addform.html')
    return template(master=master)

@bobo.post('/add')
def add(quote, name, city, state):
    rand = random.random()
    new_quote = Quotes(quote=quote, name=name, city=city,
                       state=state, rand=rand, location='0,0')
    new_quote.put()
    return bobo.redirect('/q/'+str(new_quote.key().id()))
