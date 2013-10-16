from datetime import datetime

from django import template
from django.conf import settings

from dulwich.repo import Repo
from djangit.utils import seperate_tree_entries, get_author, get_repo_path

register = template.Library()


@register.inclusion_tag('djangit/includes/commit_info.html')
def djangit_commit_info(repo_name, identifier, link_to_tree=False):

    repo = Repo(get_repo_path(repo_name))

    if len(identifier) == 40:
        # It's a SHA
        commit = repo[identifier]
    else:
        # It's probably not a SHA
        commit = repo[repo.ref('refs/heads/' + identifier)]

    author = get_author(commit)

    commit_time = datetime.fromtimestamp(commit.commit_time)

    return {
        'commit': commit,
        'author': author,
        'commit_time': commit_time,
        'repo_name': repo_name,
        'link_to_tree': link_to_tree,
    }


@register.inclusion_tag('djangit/includes/tree.html')
def djangit_tree(repo_name, identifier, path=None, show_readme=True):

    context = {}

    repo = Repo(get_repo_path(repo_name))

    # Check if the identifier is 40 chars, if so it must be a sha
    if len(identifier) == 40:
        tree = repo[identifier]
    # else it's just a normal reference name.
    else:
        tree = repo[repo['refs/heads/' + identifier].tree]

    if path:
        for part in path.split('/'):
            tree = repo[tree[part][1]]

    if show_readme:
        if 'README.markdown' in tree:
            context['readme'] = repo[tree['README.markdown'][1]]
        elif 'README.md' in tree:
            context['readme'] = repo[tree['README.md'][1]]

    trees, blobs = seperate_tree_entries(tree, path, repo)

    context.update({
        'repo_name': repo_name,
        'identifier': identifier,
        'trees': trees,
        'blobs': blobs,
    })

    return context

@register.inclusion_tag('djangit/includes/breadcrumb.html')
def djangit_breadcrumb(repo_name, tree):
    pass

@register.inclusion_tag('djangit/includes/breadcrumb.html')
def djangit_repo_info(repo_name):
    pass
