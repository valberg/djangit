from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',

    url(r'^(?P<name>[^/]+)/commits/(?P<identifier>[^/]*)/$',
        views.RepositoryListCommits.as_view(), name='list_commits'),

    url(r'^(?P<name>[^/]+)/tree/(?P<identifier>[^/]*)/(?P<path>.*)$',
        views.RepositoryShowTree.as_view(), name='show_tree'),

    url(r'^(?P<name>[^/]+)/blob/(?P<identifier>[^/]*)/(?P<path>.*)$',
        views.RepositoryShowBlob.as_view(), name='show_blob'),

    url(r'^(?P<name>[^/]+)/commit/(?P<sha>\w{40})$',
        views.RepositoryShowCommit.as_view(), name='show_commit'),

    url(r'^(?P<name>[^/]+)/(?P<identifier>[^/]+)$',
        views.RepositoryDetail.as_view(), name='show_repo'),

    url(r'^create_repo/',
        views.CreateRepoView.as_view(), name='create_repo'),

    url(r'^$',
        views.RepositoryList.as_view(), name='list_repos'),
)
