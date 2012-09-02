from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'', include('blogApp.users.urls')),
    (r'', include('blogApp.posts.urls')),
)
