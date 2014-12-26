from django import forms

from .models import Repository


class CreateRepoForm(forms.ModelForm):
    """
    Form for creation of new repositories.
    """

    initial_commit = forms.BooleanField(required=False)

    class Meta:
        model = Repository
        fields = ['name', 'description', 'initial_commit']

    def clean_name(self):
        return self.cleaned_data['name'].replace(' ', '-')
