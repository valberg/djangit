from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',

    url(r'^(?P<repo_name>[^/]+)/commits/(?P<identifier>[^/]*)/$',
        views.list_commits, name='list_commits'),

    url(r'^(?P<repo_name>[^/]+)/tree/(?P<identifier>[^/]*)/(?P<path>.*)$',
        views.show_tree, name='show_tree'),

    url(r'^(?P<repo_name>[^/]+)/blob/(?P<identifier>[^/]*)/(?P<path>.*)$',
        views.show_blob, name='show_blob'),

    url(r'^(?P<repo_name>[^/]+)/blob/(?P<blob1_sha>\w{40}):(?P<blob2_sha>\w{40})$',
        views.show_blob_diff, name='show_blob_diff'),

    url(r'^(?P<repo_name>[^/]+)/commit/(?P<sha>\w{40})$',
        views.show_commit, name='show_commit'),

    url(r'^(?P<repo_name>[^/]+)/(?P<identifier>[^/]+)$',
        views.show_repo, name='show_repo'),

    url(r'^create_repo/', views.CreateRepoView.as_view(), name='create_repo'),

    url(r'^$', views.list_repos, name='list_repos'),
)
