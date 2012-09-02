from google.appengine.ext import db

from blogApp.utils import delete_objects
from blogApp.users.models import User


class Post(db.Model):
    title = db.StringProperty()
    intro = db.StringProperty()
    slug = db.StringProperty()
    content = db.StringProperty(multiline=True, indexed=True)
    last_edited = db.DateTimeProperty(auto_now=True)
    date_created = db.DateTimeProperty()
    user = db.ReferenceProperty(User)
    published = db.BooleanProperty(default=False)

    def delete_post(self):
        delete_objects(self.comments)
        self.delete()


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name="comments")
    date = db.DateProperty(auto_now_add=True)
    content = db.StringProperty(multiline=True, indexed=True)
