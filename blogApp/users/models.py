# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password, check_password

from google.appengine.ext import db


class UserException(Exception):
    pass


def normalizeemail(email):
    # Normalize the address by lowercasing the domain part of the email
    # address.
    return email.strip().lower()


class User(db.Model):
    Exception = UserException
    """ User model, uses email as the objects key_name to guarantee uniqueness."""

    reg_date = db.DateTimeProperty(auto_now_add=True)
    password = db.StringProperty(indexed=False)
    email = db.EmailProperty(required=True)
    terms_accepted = db.BooleanProperty(default=True, indexed=False)
    nick = db.StringProperty()
    last_login = db.DateTimeProperty(auto_now_add=True)
    is_admin = db.BooleanProperty()

    @property
    def id(self):
        try:
            return self.key().id()
        except db.NotSavedError:
            return None

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.put()
        return check_password(raw_password, self.password, setter)

    @classmethod
    def create_user(cls, email, password):
        """ Creates and saves a User with the given e-mail and password."""
        email = normalizeemail(email)
        u = User.all(keys_only=True).filter('email =', email).fetch(1)
        if u:
            return
        user = User(email=email)
        user = user.set_is_admin()
        user.set_password(password)
        user.is_active = False
        user.terms_accepted = True
        user.put()
        return user

    def set_is_admin(self):
        if self.email is None:
            self.is_admin = False
            return self
        if self.email in settings.ADMINS_EMAILS:
            self.is_admin = True
            return self

    @classmethod
    def email_can_be_registered(cls, email):
        if email in settings.ADMINS_EMAILS:
            return True
        return False


# modified django-registration's simplebackend
class Backend(object):
    """ A registration backend which implements the simplest possible workflow.

    A user supplies a username, email address and password
    (the bare minimum for a useful account), and is immediately signed
    up and logged in."""

    def register(self, request, **kwargs):
        """ Create and immediately log in a new user."""

        email, password = kwargs['email'], kwargs['password1']
        new_user = User.create_user(email, password)
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        return new_user

    def get_user(self, user_id):
        user = User.get_by_id(user_id)
        if user:
            return user
        return None

    def authenticate(self, email=None, password=None):
        users = User.all().filter('email =', email).fetch(limit=1)
        if users:
            user = users[0]
            if user.check_password(password):
                return user
        return None

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def post_registration_redirect(self, request, user):
        """
        After registration, redirect to the user's account page.

        """
        return ('post_dashboard', (), {})

    def post_activation_redirect(self, request, user):
        raise NotImplementedError

    def activate(self, **kwargs):
        raise NotImplementedError
