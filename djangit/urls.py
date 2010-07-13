from django.conf.urls.defaults import *
from djangit.views import *

urlpatterns = patterns('',
    
    (r'^(?P<repo>[^/]*)/commits/(?P<ref>[^/]*)/$', list_commits),
    
    (r'^(?P<repo>[^/]*)/tree/(?P<ref>[^/]*)/(?P<tree>.*)$', show_tree),
    
    (r'^(?P<repo>[^/]*)/blob/(?P<ref>[^/]*)/(?P<blob>.*)$', show_blob),
    
    (r'^(?P<repo>[^/]*)/commit/(?P<ref>[^/]*)/(?P<sha>\w{40})$', show_commit),
    
    (r'^(?P<repo>[^/]*)/(?P<ref>[^/]*)$', show_repo),
    
    (r'^$', list_repos),
)
