import re
from google.appengine.ext import db

from blogApp.users.models import User


class Post(db.Model):
    title = db.StringProperty()
    intro = db.TextProperty()
    slug = db.StringProperty()
    content = db.TextProperty()
    last_edited = db.DateTimeProperty(auto_now=True)
    date_created = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User)
    published = db.BooleanProperty(default=False)
    date_published = db.DateTimeProperty()

    def formated_content(self):
        """translate multiple and single EOF signs
        to html tags"""
        if not self.content:
            return ""
        content = self.content.replace('\r', '')
        paragraphs = re.split('\n{2,}', content)
        paragraphs_joined = "</p><p>".join(paragraphs)
        paragraphs = "<p>" + paragraphs_joined + "</p>"

        lines = re.split('\n', paragraphs)
        lines_joined = "</br>".join(lines)
        return lines_joined
