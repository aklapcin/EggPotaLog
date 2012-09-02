from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from django.views.generic import TemplateView

from blogApp.users import forms
from blogApp.users.views import adminIntro


urlpatterns = patterns('',
    url(r'^admin$', adminIntro.as_view(), name="adminIntro"),

    url(r'^admin/login/$', 'blogApp.users.views.login',
        kwargs={'authentication_form': forms.AuthenticationForm}, name="blog_login"),

    url(r'^admin/logout/$', 'django.contrib.auth.views.logout',
        kwargs={'next_page': '/'}, name="gblog_logout"),

    url(r'^admin/register/$', 'analysisGrid.users.views.register', \
        kwargs={'form_class': forms.RegistrationForm}, name="blog_register"),

    url(r'^admin/disallowed/$', direct_to_template, \
        kwargs={'template': 'users/disallowed.html'}, name="registration_disallowed"),
)
