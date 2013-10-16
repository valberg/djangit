from datetime import datetime

from django import template

from dulwich.repo import Repo

from djangit import utils

register = template.Library()


@register.inclusion_tag('djangit/includes/commit_info.html')
def djangit_commit_info(repo, identifier, link_to_tree=False):

    repo = repo.get_repo_object()

    if len(identifier) == 40:
        # It's a SHA
        commit = repo[identifier]
    else:
        # It's probably not a SHA
        commit = repo[repo.ref('refs/heads/' + identifier)]

    commit_time = datetime.fromtimestamp(commit.commit_time)

    return {
        'commit': commit,
        'commit_time': commit_time,
        'link_to_tree': link_to_tree,
    }


@register.inclusion_tag('djangit/includes/tree.html')
def djangit_tree(repo, identifier, path=None, show_readme=True):

    context = {}

    repo_object = repo.get_repo_object()

    # Check if the identifier is 40 chars, if so it must be a sha
    if len(identifier) == 40:
        tree = repo_object[identifier]
    # else it's just a normal reference name.
    else:
        tree = repo_object[repo_object['refs/heads/' + identifier].tree]

    if path:
        for part in path.split('/'):
            tree = repo_object[tree[part][1]]

    if show_readme:
        if 'README.markdown' in tree:
            context['readme'] = repo_object[tree['README.markdown'][1]]
        elif 'README.md' in tree:
            context['readme'] = repo_object[tree['README.md'][1]]

    trees, blobs = utils.seperate_tree_entries(tree, repo_object, path=path)

    context.update({
        'trees': trees,
        'blobs': blobs,
        'repo_name': repo.name,
        'identifier': identifier,
    })

    return context

@register.inclusion_tag('djangit/includes/breadcrumb.html')
def djangit_breadcrumb(repo_name, tree):
    pass

@register.inclusion_tag('djangit/includes/breadcrumb.html')
def djangit_repo_info(repo_name):
    pass

@register.inclusion_tag('djangit/includes/branch_picker.html')
def djangit_branch_picker(repo_name):
    pass

@register.filter
def djangit_format_author(author):
    if len(author) > 0:
        ms = author.index('<')
        name = author[:ms].strip(' ')
        email = author[ms + 1:-1]
    else:
        name = 'Unknown'
        email = 'Unknown'

    author = {
        'name': name,
        'email': email,
    }

    return author
