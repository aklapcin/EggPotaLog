# -*- coding: UTF-8 -*-


from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm


from blogApp.users.models import User, normalizeemail


attrs_dict = {'class': 'required'}


class EmailPasswordResetForm(PasswordResetForm):

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.user = None
        user = User.all().filter('email =', email).run(limit=1)
        if user:
            self.user = user[0]
        if self.user is None:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75,
                                                               placeholder="Type your e-mail address")),
                             label=_("Email address"))

    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict,
                                                                placeholder='Type your password')),
                               label=_("Password"))

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email and password."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    """ Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend."""
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75,
                                                               placeholder="Type your e-mail address")),
                             label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict,
                                                                    placeholder="Type your password"),
                                render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict,
                                                                    placeholder="Retype your password"),
                                render_value=False),
                                label=_("Password (again)"))

    def clean_email(self):
        email = normalizeemail(self.cleaned_data['email'])
        user = User.all().filter('email =', email).fetch(limit=1)
        if user:
            raise forms.ValidationError(_(u"This email address is already registered"))

        if email not in settings.ADMINS_EMAILS:
            raise forms.ValidationError(_(u"Can not register user with given email"))

        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data
