"""
Views which allow users to create and activate accounts.

"""
import logging
import urlparse
import datetime
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib.auth import get_backends
from django.http import HttpResponseRedirect

from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from google.appengine.ext import deferred

from blogApp.users.models import User
from blogApp.users.forms import AuthenticationForm


def register(request, backend=None, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='users/register.html',
             extra_context=None):
    """
    Allow a new user to register an account.

    The actual registration of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    it will be used as follows:

    1. The backend's ``registration_allowed()`` method will be called,
       passing the ``HttpRequest``, to determine whether registration
       of an account is to be allowed; if not, a redirect is issued to
       the view corresponding to the named URL pattern
       ``registration_disallowed``. To override this, see the list of
       optional arguments for this view (below).

    2. The form to use for account registration will be obtained by
       calling the backend's ``get_form_class()`` method, passing the
       ``HttpRequest``. To override this, see the list of optional
       arguments for this view (below).

    3. If valid, the form's ``cleaned_data`` will be passed (as
       keyword arguments, and along with the ``HttpRequest``) to the
       backend's ``register()`` method, which should return the new
       ``User`` object.

    4. Upon successful registration, the backend's
       ``post_registration_redirect()`` method will be called, passing
       the ``HttpRequest`` and the new ``User``, to determine the URL
       to redirect the user to. To override this, see the list of
       optional arguments for this view (below).

    **Required arguments**

    None.

    **Optional arguments**

    ``backend``
        The dotted Python import path to the backend class to use.

    ``disallowed_url``
        URL to redirect to if registration is not permitted for the
        current ``HttpRequest``. Must be a value which can legally be
        passed to ``django.shortcuts.redirect``. If not supplied, this
        will be whatever URL corresponds to the named URL pattern
        ``registration_disallowed``.

    ``form_class``
        The form class to use for registration. If not supplied, this
        will be retrieved from the registration backend.

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``success_url``
        URL to redirect to after successful registration. Must be a
        value which can legally be passed to
        ``django.shortcuts.redirect``. If not supplied, this will be
        retrieved from the registration backend.

    ``template_name``
        A custom template to use. If not supplied, this will default
        to ``registration/registration_form.html``.

    **Context:**

    ``form``
        The registration form.

    Any extra variables supplied in the ``extra_context`` argument
    (see above).

    **Template:**

    registration/registration_form.html or ``template_name`` keyword
    argument.

    """
    backend = get_backends()[0]
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                new_user = backend.register(request, **form.cleaned_data)
            except User.Exception, e:
                logging.error("RegistrationError: %s", e)
                return redirect(disallowed_url)
            except Exception, e:
                logging.error("RegistrationError: %s" % e.message)
                #FIXME: add msg for user explaining an error occured
            else:
                if success_url is None:
                    to, args, kwargs = backend.post_registration_redirect(request, new_user)
                    return redirect(to, *args, **kwargs)
                else:
                    return redirect(success_url)
    else:
        data = None
        if hasattr(form_class, 'initial_from_request'):
            data = form_class.initial_from_request(request)
        form = form_class(initial=data)

    if extra_context is None:
        extra_context = {}

    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)


@csrf_protect
@never_cache
def login(request, template_name='users/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            user = form.get_user()
            user.last_login = datetime.datetime.now()
            user.put()
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)
    request.session.set_test_cookie()
    context = {
        'form': form,
        redirect_field_name: redirect_to
    }
    if extra_context is not None:
        context.update(extra_context)
    a = TemplateResponse(request, template_name, context)
    return a


class adminIntro(TemplateView):
    template_name = "users/admin.html"

    def get(self, request, *args, **kwargs):
        return super(adminIntro, self).get(request, *args, **kwargs)
