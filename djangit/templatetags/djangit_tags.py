from datetime import datetime
import string

from django import template

from dulwich.repo import Repo

from djangit import utils

register = template.Library()


@register.inclusion_tag('djangit/includes/commit_info.html')
def djangit_commit_info(repo, identifier, link_to_tree=False,
                        include_parent=False):
    """
    Show info about a commit.

    :param repo: A Repository model instance which has the commit.
    :param identifier: The identifier for the commit.
    :param link_to_tree: A boolean that defines whether to show a link to the
        tree of the commit or not.
    """

    repo_object = repo.get_repo_object()

    try:
        commit = utils.get_commit(repo_object, identifier)
        commit_time = None
        if commit:
            commit_time = datetime.fromtimestamp(commit.commit_time)
    except KeyError:
        commit = None
        commit_time = None

    return {
        'commit': commit,
        'commit_time': commit_time,
        'author': commit.author,
        'link_to_tree': link_to_tree,
        'repo_name': repo.name,
        'include_parent': include_parent,
    }


@register.inclusion_tag('djangit/includes/tree.html')
def djangit_tree(repo, identifier, path=None, show_readme=True):
    """
    Show a tree.


    :param repo: A Repository model instance which has the tree.
    :param identifier: The identifier for the tree.
    :param path: What path to show. If None the root will be shown.
    :param show_readme: Whether to check for a README file and show it below the tree.
    """

    context = {}
    repo_object = repo.get_repo_object()

    no_tree = True
    trees = None
    blobs = None

    try:
        try:
            tree = repo_object[utils.get_commit(repo_object, identifier).tree]
        except AttributeError:
            try:
                tree = repo_object[utils.get_commit(repo_object, identifier).id]
            except AttributeError:
                tree = None

        if tree:
            if path:
                for part in path.split('/'):
                    tree = repo_object[tree[part][1]]

            if show_readme:
                if 'README.markdown' in tree:
                    context['readme'] = repo_object[tree['README.markdown'][1]]
                elif 'README.md' in tree:
                    context['readme'] = repo_object[tree['README.md'][1]]

            no_tree = False
            trees, blobs = utils.seperate_tree_entries(
                tree, repo_object, path=path)

    except KeyError:
        trees = None
        blobs = None
        no_tree = True

    context.update({
        'no_tree': no_tree,
        'trees': trees,
        'blobs': blobs,
        'repo_name': repo.name,
        'identifier': identifier,
    })

    return context

@register.inclusion_tag('djangit/includes/breadcrumb.html')
def djangit_breadcrumb(repo, identifier, path=None):
    """
    Show a breadcrumb for the current location in the tree.

    :param repo: Which repository.
    :param identifier: Identifier for the ref.
    :param path: What path to show. If None the root will be shown.
    """

    context = {
        'repo': repo,
        'identifier': identifier,
    }

    repo_object = repo.get_repo_object()

    try:
        tree = utils.get_commit(repo_object, identifier)
    except KeyError:
        tree = None

    if tree:
        crumbs = []

        path_parts = path.split('/')

        for i in range(len(path_parts)):
            name = path_parts[i]

            # TODO: This is somewhat hackish.
            if i == 0:
                path_template = '{}{}'
            else:
                path_template = '{}/{}'

            link_path = path_template.format(string.join(path_parts[:i], '/'), name)

            crumbs.append((name, link_path))

        context['crumbs'] = crumbs

    return context

@register.inclusion_tag('djangit/includes/repo_info.html')
def djangit_repo_info(repo):
    """
    Show general information about a repo.

    :param repo: Model instance for the repo that should be shown.
    """

    context = {
        'repo': repo,
    }

    return context

@register.inclusion_tag('djangit/includes/ref_picker.html')
def djangit_ref_picker(repo, identifier, path=None):
    """
    List all references.

    :params repo: Model instance for the repo whose references should be shown
    :params identifier: Identifier of the current ref
    :params path: Which path to link to.
    """

    context = {
        'repo': repo,
        'identifier': identifier,
        'path': path
    }

    return context

@register.filter
def djangit_format_author(author):
    """
    Get name and email from a string like this: "Name <email>"
    """
    name = 'Unknown'
    email = 'Unknown'

    if len(author) > 0:
        try:
            ms = author.index('<')
            name = author[:ms].strip(' ')
            email = author[ms + 1:-1]
        except ValueError:
            if author == 'Djangit':
                name = author
                email = ''

    author = {
        'name': name,
        'email': email,
    }

    return author
