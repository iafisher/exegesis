from django import forms


class ImportProjectForm(forms.Form):
    username = forms.CharField(label='Username of repository owner',
        max_length=127)
    reponame = forms.CharField(label='Repository', max_length=128)
    sha = forms.CharField(label='Commit hash', max_length=100)
