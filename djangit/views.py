import difflib
from django.core.urlresolvers import reverse
from django.views.generic import FormView, ListView, DetailView

from dulwich.repo import Repo, Tree
from dulwich.walk import Walker

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings

from . import models, utils, forms


class RepositoryView(DetailView):
    context_object_name = 'repo'

    def get_object(self):
        name = self.kwargs['name']
        return models.Repository.objects.get(name=name)

    def get_context_data(self, **kwargs):
        context = super(RepositoryView, self).get_context_data(**kwargs)

        # We always want to send the stuff from the URL to the template
        context.update(self.kwargs)

        return context


class RepositoryDetail(RepositoryView):
    template_name = 'djangit/show_repo.html'


class RepositoryShowTree(RepositoryView):
    template_name = 'djangit/show_tree.html'


class RepositoryList(ListView):
    model = models.Repository
    template_name = 'djangit/list_repos.html'
    context_object_name = 'repos'


def list_commits(request, repo_name, identifier):
    """ List all commits for ref

    Creates a repo objects using repo_name, and gets revision history, that is
    all commits, of the provided identifier.
    """

    repo = Repo(settings.GIT_REPOS_DIR + repo_name + '.git')

    # Since revision_history wants the whole name of the reference, incl.
    # the refs/head/ part we need to prepend that to the identifier.

    walker = Walker(repo, [repo.head()])

    commits = [commit.commit for commit in walker]

    return render_to_response('djangit/list_commits.html', {
        'repo_name': repo_name,
        'identifier': identifier,
        'commits': commits,
    }, context_instance=RequestContext(request))


def show_blob(request, repo_name, identifier, path):
    """ Show blob
    Creates a repo object, checks if it comes from a normal name or sha value
    identifier, finds it's way to the right tree (which actually in the end is
    a blob, so it is quite misleading that we are calling the variable a tree)
    and then in the end render_to_response to show the world this blobby blob!

    Another quite confusing thing is that when checking out a tree from a SHA,
    the identifier is of course the tree, and therefore commit is a tree.
    """

    repo = Repo(settings.GIT_REPOS_DIR + repo_name + '.git')

    context = {}

    if len(identifier) == 40:
        commit = repo[identifier]

        # Quite a hack, there must be a more elegant way of doing this
        if commit.__class__ == Tree:
            tree = repo[commit.id]
        else:
            tree = repo[commit.tree]

    else:
        tree = repo[repo['refs/heads/' + identifier].tree]

    for part in path.split('/'):
        part = part.encode('utf-8')
        tree = repo[tree[part][1]]

    filext = path.split('/')[-1].split('.')[-1]

    markdown = False
    if filext in ['markdown', 'md']:
        markdown = True

    if markdown:
        blob = tree
    else:
        blob = str(tree).split('\n')
        context['linecount'] = range(1, len(blob))

    context.update({
        'repo_name': repo_name,
        'blob': blob,
        'markdown': markdown,
        'tree_path': path
    })

    return render_to_response(
        'djangit/show_blob.html',
        context,
        context_instance=RequestContext(request)
    )


def show_commit(request, repo_name, sha):
    """ Show commit

    Pretty straight forward:
    1. create a repo object
    2. find commit via sha value
    3. use render_to_response to show the world!

    TODO: write the part that finds the diff's into a function of it's own!
    """

    repo = Repo(settings.GIT_REPOS_DIR + repo_name + '.git')

    obj_store = repo.object_store

    commit = repo[sha]

    if commit.parents:
        # Right now we only support single parents
        commit_parent = repo[commit.parents[0]]
        changes = obj_store.tree_changes(commit.tree, commit_parent.tree)

        diffs = make_diffs(changes, repo)
    else:
        diffs = []
        for entry in obj_store.iter_tree_contents(commit.tree):
            blob = repo[entry[2]]
            diffs.append((entry[0], blob._get_data()))

    return render_to_response('djangit/show_commit.html', {
        'repo_name': repo_name,
        'sha': sha,
        'diffs': diffs,
    }, context_instance=RequestContext(request))


def make_diffs(changes, repo):
    """
    Create diffs for two different commits
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


def show_blob_diff(request, repo_name, blob1_sha, blob2_sha):
    ''' Show blob diff's using difflib
    TODO: this view need some love and understanding

    '''
    repo = Repo(settings.GIT_REPOS_DIR + repo_name + '.git')

    blob1 = repo[blob1_sha]
    blob2 = repo[blob2_sha]

    # Check if there already exists a cache of the diff
    # If so, use that file
    # To be implemented :P

    # htmldiffer = difflib.HtmlDiff()
    # diff_html = htmldiffer.make_table(blob1.data.split('\n'),
    #                                  blob2.data.split('\n'))

    diff = difflib.context_diff(blob2.data.split('\n'),
                                blob1.data.split('\n'))

    diff_string = ""
    for line in diff:
        diff_string += line + '\n'

    return render_to_response('djangit/show_blob_diff.html', {
        'repo_name': repo_name,
        'blob1': blob1,
        'blob2': blob2,
        'diff': diff_string,
    }, context_instance=RequestContext(request))


class CreateRepoView(FormView):
    form_class = forms.CreateRepoForm
    template_name = 'djangit/create_repo.html'

    def form_valid(self, form):
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        initial_commit = form.cleaned_data['initial_commit']

        repo = models.Repository(
            name=name,
            description=description,
        )

        repo.save(initial_commit=initial_commit)

        return redirect(reverse('djangit:list_repos'))
