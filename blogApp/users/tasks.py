from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string

from google.appengine.api import mail

import cryptutils

from analysisGrid.users.models import User
from analysisGrid.grid.models import Grid



def send_password_reset_email(user=None):
    if user is None:
        return

    token = default_token_generator.make_token(user)
    user_key = str(user.key())
    enc_key = cryptutils.encrypt(user_key)
    url = reverse('forgotten_password_change', kwargs={'user_key': enc_key, 'token': token})
    host = settings.HTTP_HOST

    ctx_dict = {
        'url': url,
        'host': host
    }

    message_html = render_to_string('user/password_change_email.html', ctx_dict)

    mesg = mail.EmailMessage()
    mesg.sender = settings.OPINIONGRID_EMAIL_SENDER + " <" + settings.OPINIONGRID_EMAIL_ADDRESS + ">"
    mesg.subject = settings.CHANGE_PASSWORD_EMAIL_SUBJECT
    mesg.to = user.email

    mesg.body = message_html

    mesg.send()


def connect_grids_to_user(user_key=None):
    if user_key is None:
        return
    user = User.get(user_key)
    email = user.email
    grids = Grid.all().filter('user_email = ', email).fetch(1000)
    count = 0
    for g in grids:
        g.user = user
        g.put()
        count += 1
    user.free_grids = count
    user.put()


def delete_user(user_key=None):
    if user_key is None:
        return
    user = User.get(user_key)
    if user is None:
        return
    user.delete_user()
