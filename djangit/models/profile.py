from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .mixins import TimeStampedModel


class Profile(TimeStampedModel):

    user = models.OneToOneField('auth.User')

    class Meta:
        verbose_name = 'Djangit Profile'
        verbose_name_plural = 'Djangit Profiles'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )
