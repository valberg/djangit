import os
from time import time

from django.conf import settings

from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from dulwich.client import get_transport_and_path


def get_repo_path(repo_name):
    return os.path.join(settings.GIT_REPOS_DIR, '{}.git'.format(repo_name))


def seperate_tree_entries(tree, repo, path=None):
    """ Seperates tree entries

    Iterates through the tree entries to place trees in one list and blobs in
    another depending on the entrys type_num.

    """
    trees = []
    blobs = []

    for name, mode, sha in tree.iteritems():
        if path:
            url = path + '/' + name.decode('utf-8')
        else:
            url = name.decode('utf-8')

        entry = repo.get_object(sha)

        if entry.type_num == 2:
            trees.append((mode, name, url, sha))
        elif entry.type_num == 3:
            blobs.append((mode, name, url, sha))

    return trees, blobs


def create_repo(repo_name, description=None, initial_commit=False):
    """
    Create a repository at settings.GIT_REPOS_DIR + repo_name + '.git'
    """

    repo_bare_path = get_repo_path(repo_name)

    os.makedirs(repo_bare_path)

    repo = Repo.create(repo_bare_path)

    # Write the description to the file for the time being:
    with open(os.path.join(repo_bare_path, 'description'), 'w') as f:
        if description:
            f.write(description)
        else:
            f.write(repo_name)

    if initial_commit:

        # Since we are creating a bare repo, we have to clone the repository
        # and then do the commit and then push and then remove the clone.

        readme = Blob.from_string('# {}'.format(repo_name))

        tree = Tree()
        tree.add('README.md', 0100644, readme.id)

        repo.do_commit(
            message='Initial commit',
            tree=tree.id
        )

        object_store = repo.object_store
        object_store.add_object(readme)
        object_store.add_object(tree)

        #repo.refs['refs/heads/master'] = commit.id

    return repo
