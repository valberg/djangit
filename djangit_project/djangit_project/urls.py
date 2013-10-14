from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('djangit.urls', namespace='djangit', app_name='djangit')),
)
