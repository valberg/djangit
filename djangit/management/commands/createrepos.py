from __future__ import print_function

import os
import re
import glob

from django.core.management.base import BaseCommand
from django.conf import settings

from djangit.models import DjangitRepository


class Command(BaseCommand):
    help = "Load local repositories into Djangit database."

    def handle(self, *args, **options):
        for directory in glob.glob(os.path.join(settings.GIT_REPOS_DIR, '*.git')):
            repo_name = re.search('(?P<dir>[^/]*)\.git$', directory).group('dir')
            if not DjangitRepository.objects.filter(name=repo_name).exists():
                print("Saving {}".format(repo_name), end='')
                repo = DjangitRepository(name=repo_name)
                repo.save(no_dir=True)
                print(" ... saved!".format(repo_name))
            else:
                print("{} is already in Djangit!".format(repo_name))
