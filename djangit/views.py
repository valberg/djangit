from django.shortcuts import render_to_response
from djangit import config


import dulwich
import re, glob, os

def list_repos(request):
    """ List all repos """

    repos = []

    for dir in glob.glob( os.path.join(config.GIT_REPOS_DIR, '*.git') ):
        repo_name = re.search('(?P<dir>[^/]*)\.git$', dir)
        repos.append(repo_name.group('dir'))

    return render_to_response('djangit/list_repos.html', {'repos':repos})

def show_repo(request, repo, ref):
    """ Show info about a repo """

    r = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo + '.git')

    commit = r[r.ref('refs/heads/' + ref)]
    tree = r[commit.tree]
    tree_entries = tree.entries()

    trees = []
    blobs = []

    for mode, name, sha in tree_entries:
        e = r.get_object(sha)
        if e.type_num == 2:
            url = name
            trees.append((mode, name, url, sha))
        elif e.type_num == 3:
            url = name
            blobs.append((mode, name, url, sha))

    # References

    refs = []
    
    for e in r.refs.as_dict():
        if e == "HEAD":
            pass
        else:
            m = e.split('/')
            refs.append(m[-1])

    return render_to_response('djangit/show_repo.html', {
        'repo':repo, 
        'ref':ref,
        'commit':commit,
        'refs':refs,
        'trees':trees,
        'blobs':blobs,
    })

def list_commits(request, repo, ref):
    """ List all commits for ref """

    r = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo + '.git')

    commits = r.revision_history('refs/heads/' +ref)
    
    return render_to_response('djangit/list_commits.html', {
        'repo':repo,
        'ref':ref,
        'commits':commits,
    })

def show_tree(request, repo, ref, tree):
    """ Show tree """

    r = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo + '.git')

    if len(ref) == 40:
        c = r[ref]
        t = r[c.tree]
    else:
        t = r[r['refs/heads/' + ref].tree]

    if tree:
        for p in tree.split('/'):
            t = r[t[p][1]]

    tree_entries = t.entries()
    
    trees = []
    blobs = []

    for mode, name, sha in tree_entries:
        e = r.get_object(sha)
        if e.type_num == 2:
            if tree:
                url = tree+'/'+name
            else:
                url = name
            trees.append((mode, name, url, sha))
        elif e.type_num == 3:
            if tree:
                url = tree + '/' + name
            else:
                url = name
            blobs.append((mode, name, url, sha))

    return render_to_response('djangit/show_tree.html', {
        'repo': repo,
        'ref': ref,
        'tree': tree,
        'trees': trees,
        'blobs': blobs,
    })

def show_blob(request, repo, ref, blob):
    """ Show blob """

    r = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo + '.git')
    
    if len(ref) == 40:
        c = r[ref]
        t = r[c.tree]
    else:
        t = r[r['refs/heads/' + ref].tree]

    for p in blob.split('/'):
        t = r[t[p][1]]
    
    return render_to_response('djangit/show_blob.html', { 
        'repo': repo,
        'blob': t,
    })

def show_commit(request, repo, ref, sha):
    """ Show commit """
    
    r = dulwich.repo.Repo(config.GIT_REPOS_DIR + repo + '.git')

    commit = r[sha]

    return render_to_response('djangit/show_commit.html', {
        'repo': repo,
        'ref': ref,
        'commit': commit,
    })
