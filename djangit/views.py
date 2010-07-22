from django.shortcuts import render_to_response
from djangit import config

import dulwich
import re
import glob
import os
import difflib


def seperate_tree_entries(tree_entries, tree_path, repo):
    """ Seperates tree entries

    Iterates through the tree entries to place trees in one list and blobs in
    another depending on the entrys type_num.

    """
    trees = []
    blobs = []

    for mode, name, sha in tree_entries:
        if tree_path:
            url = tree_path + '/' + name
        else:
            url = name

        entry = repo.get_object(sha)

        if entry.type_num == 2:
            trees.append((mode, name, url, sha))
        elif entry.type_num == 3:
            blobs.append((mode, name, url, sha))

    return trees, blobs


def list_repos(request):
    """ List all repos

    Globs for all directories ending in .git in GIT_REPOS_DIR and then runs a
    regex on the path of each directory to get only the name of the directory.

    Finally puts each directory in a list, 'repos', which gets sent as context
    via render_to_response.
    """

    repos = []

    for dir in glob.glob(os.path.join(config.GIT_REPOS_DIR, '*.git')):
        try:
            repo_name = re.search('(?P<dir>[^/]*)\.git$', dir)

            repo = dulwich.repo.Repo(config.GIT_REPOS_DIR +
                    repo_name.group('dir') + '.git')
            commit = repo[repo.head()]

            repos.append((repo_name.group('dir'), commit.message))
        except:
            pass

    return render_to_response('djangit/list_repos.html', {'repos': repos})


def show_repo(request, repo_name, ref_name):
    """ Show info about a repo

    Creates a repo object using repo_name, gets the latest commit and
    corresponding tree and tree entries.

    Procedes onto references of the repo. Currently 'HEAD' isn't used for
    anything, so this is gently "passed out", and since references are
    displayed as refs/heads/<name> each reference is split, and only the last
    part is put into a list, 'refs'.

    All this is then sent into space with render_to_response, incl. repo_name
    and ref_name which come from the URL.
    """

    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    # Getting the latest commit.
    commit = repo[repo.ref('refs/heads/' + ref_name)]

    # Getting the tree of latest commit.
    tree = repo[commit.tree]

    # Getting entries from the tree.
    tree_entries = tree.entries()

    trees, blobs = seperate_tree_entries(tree_entries, "", repo)

    # References
    refs = []

    for ref in repo.refs.as_dict():
        if ref == "HEAD":
            # Currently we do not use HEAD for anything, might come later.
            pass
        else:
            # We only want the last in ie. refs/heads/master
            parts = ref.split('/')
            refs.append(parts[-1])

    # We want to show the readme file, if it exists
    try:
        if tree['README.markdown']:
            readme = repo[tree['README.markdown'][1]]

    except:
        readme = ""

    return render_to_response('djangit/show_repo.html', {
        'repo_name': repo_name,
        'ref_name': ref_name,
        'commit': commit,
        'refs': refs,
        'trees': trees,
        'blobs': blobs,
        'readme': readme,
    })


def list_commits(request, repo_name, ref_name):
    """ List all commits for ref

    Creates a repo objects using repo_name, and gets revision history, that is
    all commits, of the provided ref_name.
    """

    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    # Since revision_history wants the whole name of the reference, incl.
    # the refs/head/ part we need to prepend that to the ref_name.
    commits = repo.revision_history('refs/heads/' + ref_name)

    return render_to_response('djangit/list_commits.html', {
        'repo_name': repo_name,
        'ref_name': ref_name,
        'commits': commits,
    })


def show_tree(request, repo_name, ref_name, tree_path):
    """ Show tree

    Creates a repo object from repo_name, checks ref_name for if it's a sha
    value or a normal name, and creates tree object accordingly (might cause
    problems for reference names with 40 characters, but those are unlikely to
    exist). Then it finds the corresponding tree entry by iterating till the
    last part of the path. Runs seperate_tree_entries and in the end
    render_to_response to show this lovely tree to the world.
    """

    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    # Check if the ref_name is 40 chars, if so it must be a sha
    if len(ref_name) == 40:
        commit = repo[ref_name]
        tree = repo[commit.tree]
    # else it's just a normal reference name.
    else:
        tree = repo[repo['refs/heads/' + ref_name].tree]

    if tree_path:
        for part in tree_path.split('/'):
            tree = repo[tree[part][1]]

    tree_entries = tree.entries()

    trees, blobs = seperate_tree_entries(tree_entries, tree_path, repo)

    return render_to_response('djangit/show_tree.html', {
        'repo_name': repo_name,
        'ref_name': ref_name,
        'tree_path': tree_path,
        'trees': trees,
        'blobs': blobs,
    })


def show_blob(request, repo_name, ref_name, blob_path):
    """ Show blob
    Creates a repo object, checks if it comes from a normal name or sha value
    ref_name, finds it's way to the right tree (which actually in the end is a
    blob, so it is quite misleading that we are calling the variable a tree)
    and then in the end render_to_response to show the world this blobby blob!
    """

    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    if len(ref_name) == 40:
        commit = repo[ref_name]
        tree = repo[commit.tree]
    else:
        tree = repo[repo['refs/heads/' + ref_name].tree]

    for part in blob_path.split('/'):
        tree = repo[tree[part][1]]

    md = re.search('\w*.markdown', blob_path.split('/')[-1])

    markdown = False

    if md:
        markdown = True

    return render_to_response('djangit/show_blob.html', {
        'repo': repo_name,
        'blob': tree,
        'markdown': markdown, })


def show_commit(request, repo_name, sha):
    """ Show commit

    Pretty straight forward:
    1. create a repo object
    2. find commit via sha value
    3. use render_to_response to show the world!
    """

    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    commit = repo[sha]

    diffs = []
    
    if commit.parents:
        # Right now we only support single parents
        commit_parent = repo[commit.parents[0]]

        obj_store = repo.object_store
        changes = obj_store.tree_changes(commit.tree, commit_parent.tree)
        
        for c in changes:
            # c[0] er en tuple med nyt navn og gammelt navn
            # c[1] er en typle med nyt mode og gammelt mode
            # c[2] er en tuple med ny sha og gammel sha

            try:
                diffs.append(difflib.context_diff(repo[c[2][0]], repo[c[2][1]]))
            except:
                pass

    return render_to_response('djangit/show_commit.html', {
        'repo_name': repo_name,
        'commit': commit,
        'diffs': diffs,
    })


def show_blob_diff(request, repo_name, blob1_sha, blob2_sha):
    ''' Show blob diff's using difflib '''
    repo = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo_name + '.git')

    blob1 = repo[blob1_sha]
    blob2 = repo[blob2_sha]

    # Check if there already exists a cache of the diff
    # If so, use that file
    # To be implemented :P

    htmldiffer = difflib.HtmlDiff()
    diff_html = htmldiffer.make_table(blob1.data.split('\n'), blob2.data.split('\n'))

    return render_to_response('djangit/show_blob_diff.html', {
        'repo_name': repo_name,
        'blob1': blob1,
        'blob2': blob2,
        'diff_html': diff_html,
    })
