import os
from django.conf import settings
from django.core.management import BaseCommand
from dulwich import log_utils
from dulwich.errors import NotGitRepository
from dulwich.repo import Repo
from dulwich.server import FileSystemBackend, TCPGitServer


class DjangitFileSystemBackend(FileSystemBackend):
    def open_repository(self, path):
        if path.startswith('/'):
            path = path[1:]
        abspath = os.path.abspath(os.path.join(self.root, path))
        if not abspath.startswith(self.root):
            raise NotGitRepository("Invalid path %r" % path)
        return Repo(abspath)


class Command(BaseCommand):
    help = "Run a simple git server to handle cloning, pushes etc."

    def handle(self, *args, **options):
        log_utils.default_logging_config()
        address = '0.0.0.0'
        port = 9418
        backend = DjangitFileSystemBackend(settings.DJANGIT_REPOS_DIR)
        server = TCPGitServer(backend, address, port)
        server.serve_forever()
