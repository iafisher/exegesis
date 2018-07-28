from django import forms


class ImportProjectForm(forms.Form):
    username = forms.CharField(label='Username of repository owner',
        max_length=100)
    reponame = forms.CharField(label='Repository', max_length=100)
    sha = forms.CharField(label='Commit hash', max_length=100)
