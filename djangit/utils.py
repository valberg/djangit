import difflib
import os

from django.conf import settings

from dulwich.repo import Repo
from dulwich.objects import Blob, Tree
from dulwich import walk


def get_repo_path(repo_name):
    return os.path.join(settings.GIT_REPOS_DIR, '{}.git'.format(repo_name))


def seperate_tree_entries(tree, repo, path=None):
    """ Seperates tree entries

    Iterates through the tree entries to place trees in one list and blobs in
    another depending on the entrys type_num.

    :param tree: The tree to iterate through.
    :param repo: The repo in which the tree is.
    :param path: Optional path. If defined then the tree will start from here.
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

    :param repo_name: Name of the new repo.
    :param description: Optional description.
    :param initial_commit: Whether to do a initial commit after creation.
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
            tree=tree.id,
            committer='Djangit'
        )

        object_store = repo.object_store
        object_store.add_object(readme)
        object_store.add_object(tree)

    return repo


def make_diffs(changes, repo):
    """
    Create diffs for two different commits.

    TODO: Needs some review.
    """
    diffs = []
    for change in changes:
        # change[0] is a tuple with new and old name
        # change[1] is a tuple with new and old mode
        # change[2] is a tuple with new and old sha

        # If there is a SHA for the new file, ie. the file hasn't been
        # deleted, then just go on and get the contents, otherwise set it
        # to an empty string for comparison
        new_sha = change[2][0]
        if new_sha:
            new_data = repo[new_sha].data.split('\n')
        else:
            new_data = ""

        # If there is a SHA for the old file, ie. the file hasn't just been
        # created, then just go on and get the contents, otherwise set it
        # to an empty string for comparison
        old_sha = change[2][1]
        if old_sha:
            old_data = repo[old_sha].data.split('\n')
        else:
            old_data = ""

        diff = difflib.unified_diff(
            old_data,
            new_data,
            fromfile=change[0][0],
            tofile=change[0][1])

        # If the file has just been altered, and not deleted or created,
        # set the blob name to a string with both new and old name.
        # Else if it's a new file, that is there is no parent name, then
        # set the blob name to "New file: <filename>"
        # Else if it's a deleted file, that is there is no child, then set
        # the blob name to "Deleted file: <filename>"
        if change[0][0] and change[0][1]:
            blob_name = change[0][0] + " -> " + change[0][1]
        elif not change[0][1]:
            blob_name = "New file: " + change[0][0]
        elif not change[0][0]:
            blob_name = "Deleted file: " + change[0][1]

        diff_string = ''
        for line in diff:
            diff_string += line + '\n'

        diffs.append((blob_name, diff_string))

    return diffs


def get_commit(repo_object, identifier):
    """
    Get a commit.

    :param repo_object: The repo object to get the commit from.
    :param identifier: Either a SHA or a reference name.
    """
    if len(identifier) == 40:
        # It's a SHA
        commit = repo_object[bytes(identifier)]
    else:
        # It's probably not a SHA
        commit = repo_object[repo_object.get_peeled('refs/heads/' + identifier)]

    return commit

def get_latest_commit_for_tree(repo_object, identifier, paths=None):
    """
    Get the latest commit to be shown for a tree.identifier

    :param repo_object: A object representing the repo we are working with.
    :param identifier: The identifier of the ref or three.
    :param paths: The path to get the latest commit for.
    """

    # TODO: This function could need some love as it is not very try in regard to the Walker object.

    commit_id = ''
    if len(identifier) != 40:
        for entry in walk.Walker(
            repo_object.object_store,
            [repo_object.head()],
            order=walk.ORDER_DATE,
            paths=paths,
            max_entries=1
        ):
            commit_id = entry.commit.id
    else:
        # It's a SHA, we think.
        for entry in walk.Walker(
            repo_object.object_store,
            [repo_object.head()],
            order=walk.ORDER_DATE,
        ):
            if entry.commit.tree == identifier:
                commit_id = entry.commit.id

    if len(commit_id) == 0:
        # TODO: Maybe we should raise some error here?
        commit_id = None

    return commit_id
