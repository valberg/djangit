from django.conf.urls.defaults import *
from djangit.views import *

urlpatterns = patterns('',
    
    (r'^(?P<repo_name>[^/]*)/commits/(?P<ref_name>[^/]*)/$', list_commits),
    
    (r'^(?P<repo_name>[^/]*)/tree/(?P<ref_name>[^/]*)/(?P<tree_path>.*)$', show_tree),
    
    (r'^(?P<repo_name>[^/]*)/blob/(?P<ref_name>[^/]*)/(?P<blob_path>.*)$', show_blob),
    
    (r'^(?P<repo_name>[^/]*)/commit/(?P<ref_name>[^/]*)/(?P<sha>\w{40})$', show_commit),
    
    (r'^(?P<repo_name>[^/]*)/(?P<ref_name>[^/]*)$', show_repo),
    
    (r'^$', list_repos),
)
