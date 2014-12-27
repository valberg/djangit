from django.conf import settings
from django.core.management import BaseCommand
from dulwich.server import FileSystemBackend
from dulwich.server import TCPGitServer


class Command(BaseCommand):
    help = "Load local repositories into Djangit database."

    def handle(self, *args, **options):
        address = '0.0.0.0'
        port = 9418
        backend = FileSystemBackend(settings.DJANGIT_GIT_REPOS)
        server = TCPGitServer(backend, address, port)
        server.serve_forever()
