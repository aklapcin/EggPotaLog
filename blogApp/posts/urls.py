from django.conf.urls.defaults import *
from django.conf import settings
from blogApp.posts import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MainPage.as_view(), {}, name='main_page'),
    url(r'^(?P<post_slug>[^/]+)$', views.ShowPost.as_view(), {}, name='show_post'),
    url(r'^admin/add$', views.NewPost.as_view(), {}, name='new_post'),
    url(r'^admin/dashboard$', views.PostDashboard.as_view(), {}, name='post_dashboard'),
    url(r'^admin/edit/(?P<post_key>[^/]+)$', views.EditPost.as_view(), {}, name='edit_post'),
    url(r'^admin/delete/(?P<post_key>[^/]+)$', views.delete_post, {}, name='delete_post'),

)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
        url(r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
        )
