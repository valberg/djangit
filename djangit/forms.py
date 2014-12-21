from django import forms

from .models import DjangitRepository


class CreateRepoForm(forms.ModelForm):
    """
    Form for creation of new repositories.
    """

    initial_commit = forms.BooleanField(required=False)

    class Meta:
        model = DjangitRepository

    def clean_name(self):
        return self.cleaned_data['name'].replace(' ', '-')
