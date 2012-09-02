from google.appengine.ext import db

from blogApp.users.models import User
from blogApp.utils import delete_objects


class Post(db.Model):
    title = db.StringProperty()
    content = db.StringProperty(multiline=True, indexed=True)
    laste_edited = db.DateTimeProperty(auto_now=True)
    date = db.DateTimeProperty()
    user = db.ReferneceProperty
    language = db.StringProperty()
    published = db.BooleanProperty()

    def delete_post(self):
        delete_objects(self.comments)
        self.delete()


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name="comments")
    date = db.DateProperty(auto_now_add=True)
    content = db.StringProperty(multiline=True, indexed=True)
