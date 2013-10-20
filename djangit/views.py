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

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)

        if 'identifier' not in self.kwargs:
            context['identifier'] = 'master'

        return context


class RepositoryList(ListView):
    model = models.Repository
    template_name = 'djangit/list_repos.html'
    context_object_name = 'repos'


class RepositoryShowCommit(RepositoryView):
    template_name = 'djangit/show_commit.html'

    def get_context_data(self, **kwargs):
        context = super(RepositoryShowCommit, self).get_context_data(**kwargs)

        repo_object = self.object.get_repo_object()
        object_store = repo_object.object_store
        commit = repo_object[self.kwargs['sha']]

        if commit.parents:
            # TODO: !!! Right now we only support single parents !!!
            commit_parent = repo_object[commit.parents[0]]
            changes = object_store.tree_changes(commit.tree, commit_parent.tree)
            diffs = utils.make_diffs(changes, repo_object)

        else:
            diffs = []
            for entry in object_store.iter_tree_contents(commit.tree):
                blob = repo_object[entry[2]]
                diffs.append((entry[0], blob._get_data()))

        context['diffs'] = diffs

        return context


class RepositoryListCommits(RepositoryView):
    template_name = 'djangit/list_commits.html'

    def get_context_data(self, **kwargs):
        context = super(RepositoryListCommits, self).get_context_data(**kwargs)

        repo_object = self.object.get_repo_object()

        try:
            walker = Walker(repo_object, [repo_object.head()])
            context['commits'] = [commit.commit for commit in walker]
        except KeyError:
            pass

        return context


class RepositoryShowBlob(RepositoryView):
    template_name = 'djangit/show_blob.html'

    def get_context_data(self, **kwargs):

        context = super(RepositoryShowBlob, self).get_context_data(**kwargs)

        identifier = self.kwargs['identifier']
        path = self.kwargs['path']

        repo = self.object.get_repo_object()

        if len(identifier) == 40:
            commit = repo[identifier]
            if type(commit) == Tree:
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
            'blob': blob,
            'markdown': markdown,
            'tree_path': path
        })

        return context


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
