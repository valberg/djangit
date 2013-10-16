from django.db import models

from utils import create_repo


class Repository(models.Model):

    name = models.CharField(
        max_length=255,
        help_text=u'Spaces will be replaces with dashes.'
    )

    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = u'Repository'
        verbose_name_plural = u'Repositories'

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, **kwargs):

        initial_commit = kwargs['initial_commit']

        super(Repository, self).save()

        create_repo(self.name, self.description, initial_commit=initial_commit)
