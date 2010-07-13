from django.conf.urls.defaults import *
from djangit.views import *

urlpatterns = patterns('',
    (r'^$', list_repos),
    (r'^(?P<repo>[^/]*)/(?P<ref>[^/]*)$', show_repo),
    (r'^(?P<repo>[^/]*)/commits/(?P<ref>[^/]*)/$', list_commits),
    
    # For latest commit - no need for SHAs
    (r'^(?P<repo>[^/]*)/tree/(?P<ref>[^/]*)/(?P<tree>.*)$', show_tree),
    (r'^(?P<repo>[^/]*)/blob/(?P<ref>[^/]*)/(?P<blob>.*)$', show_blob),
    (r'^(?P<repo>[^/]*)/commit/(?P<ref>[^/]*)/(?P<sha>\w{40})$', show_commit),
)
