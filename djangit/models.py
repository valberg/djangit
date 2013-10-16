from datetime import datetime
import os
import shutil
from django.db import models
from django.utils import timezone

from dulwich.repo import Repo

from . import utils


class Repository(models.Model):

    name = models.CharField(
        max_length=255,
        help_text=u'Spaces will be replaces with dashes.',
        unique=True,
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
        """
        Override the save method to create the actual repo when the
        model instance is created.
        """

        initial_commit = False
        if 'initial_commit' in kwargs:
            initial_commit = kwargs['initial_commit']

        super(Repository, self).save()

        # Only create the repo if the directory does not exist.
        if not os.path.exists(utils.get_repo_path(self.name)):
            utils.create_repo(self.name, self.description, initial_commit=initial_commit)


    def delete(self, using=None):
        """
        Make sure to delete the repository in the filesystem when
        deleting the model instance.

        !!! ATTENTION !!!
        This will delete the whole repository!

        """
        shutil.rmtree(utils.get_repo_path(self.name))
        super(Repository, self).delete()

    def get_repo_object(self):
        """
        Get a dulwich Repo object that is associated
        with the django model instance.
        """
        return Repo(utils.get_repo_path(self.name))

    def has_commits(self):
        """
        Check if the repo actually has any commits.
        """
        return len(self.get_repo_object().get_refs()) > 0


    def get_latest_commit(self):
        """
        Get the latest commit for the repository.
        """
        repo = self.get_repo_object()

        # TODO: Somehow it should be possible to define a
        # branch and get the latest commit for that branch.

        return repo[repo.head()]


    def get_latest_commit_time(self):
        """
        Get the datetime of the latest commit.
        """
        return datetime.fromtimestamp(self.get_latest_commit().commit_time)

    def get_refs(self):
        """
        Return refs for the repository.
        """
        refs = []

        for ref in self.get_repo_object().refs.as_dict():
            if ref == "HEAD":
                # Currently we do not use HEAD for anything, might come later.
                pass
            else:
                # We only want the last in ie. refs/heads/master
                parts = ref.split('/')
                refs.append(parts[-1])

        return refs
