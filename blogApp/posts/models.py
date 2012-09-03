from google.appengine.ext import db

from blogApp.users.models import User


class Post(db.Model):
    title = db.StringProperty()
    intro = db.StringProperty()
    slug = db.StringProperty()
    content = db.StringProperty(multiline=True, indexed=True)
    last_edited = db.DateTimeProperty(auto_now=True)
    date_created = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User)
    published = db.BooleanProperty(default=False)
    date_published = db.DateTimeProperty()
