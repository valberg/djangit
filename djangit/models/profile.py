from django.db import models

from .mixins import TimeStampedModel


class DjangitProfile(TimeStampedModel):

    user = models.OneToOneField('auth.User')

    class Meta:
        verbose_name = 'Djangit Profile'
        verbose_name_plural = 'Djangit Profiles'

    def __str__(self):
        return self.user.username

