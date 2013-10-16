import os

from django import forms

from .utils import get_repo_path


class NewRepoForm(forms.Form):
    """
    Form for creation of new repositories.
    """

    repo_name = forms.CharField()

    description = forms.CharField(
        widget=forms.Textarea()
    )

    initial_commit = forms.BooleanField()

    def clean_repo_name(self):
        """
        Check if there is already a directory with that name.
        """

        if os.path.exists(get_repo_path(self.cleaned_data['repo_name'])):
            raise forms.ValidationError('Repo already exists!')

        return self.cleaned_data['repo_name']