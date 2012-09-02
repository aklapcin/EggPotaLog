# -*- coding: UTF-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import random
import datetime
class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		random.seed()
		r=random.randint(0,1)
		
		if r==0:
			text="Idziesz zuk"
		else:
			text="Nieeee!"
		
		template_values = {'text': text,}

		
		if user:

			
			self.response.out.write(template.render("index.html", template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
		

application = webapp.WSGIApplication([('/', MainPage)],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
