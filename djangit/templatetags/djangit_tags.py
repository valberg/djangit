from datetime import datetime

from django import template

from djangit.views import get_author

register = template.Library()


@register.inclusion_tag('djangit/includes/commit_info.html')
def djangit_commit_info(commit, repo_name, link_to_tree=False):

    author = get_author(commit)

    commit_time = datetime.fromtimestamp(commit.commit_time)

    return {
        'commit': commit,
        'author': author,
        'commit_time': commit_time,
        'repo_name': repo_name,
        'link_to_tree': link_to_tree,
    }
