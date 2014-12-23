from django.contrib import admin

from . import models

admin.site.register(models.Repository)
admin.site.register(models.Profile)

