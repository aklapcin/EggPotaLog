from django.conf.urls.defaults import *
from django.conf import settings
from blogApp.posts import views

urlpatterns = patterns(
    '',
    url(r'add', views.NewPost.as_view(), {}, name='new_post'),
    url(r'dashboard', views.PostDashboard.as_view(), {}, name='dashboard'),
    url(r'edit', views.EditPost.as_view(), {}, name='edit_post'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
        url(r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
        )

