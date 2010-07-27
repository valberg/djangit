from django.conf.urls.defaults import *
from djangit.views import *

urlpatterns = patterns('',

    (r'^(?P<repo_name>[^/]*)/commits/(?P<identifier>[^/]*)/$',
        list_commits),

    (r'^(?P<repo_name>[^/]*)/tree/(?P<identifier>[^/]*)/(?P<tree_path>.*)$',
        show_tree),

    (r'^(?P<repo_name>[^/]*)/blob/(?P<identifier>[^/]*)/(?P<blob_path>.*)$',
        show_blob),

    (r'^(?P<repo_name>[^/]*)/blob/(?P<blob1_sha>\w{40}):(?P<blob2_sha>\w{40})$',
        show_blob_diff),

    (r'^(?P<repo_name>[^/]*)/commit/(?P<sha>\w{40})$',
        show_commit),

    (r'^(?P<repo_name>[^/]*)/(?P<identifier>[^/]*)$',
        show_repo),

    (r'^$', list_repos),
)
