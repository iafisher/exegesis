import base64

import requests

from .models import Directory, Project, Snippet


def download_from_github(url):
    headers = {'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response = r.json()
        # TODO: Do not assume that the file is encoded in UTF-8.
        return base64.b64decode(response['content']).decode('utf-8')
    else:
        return ''


def import_from_github(username, repo, commit_hash):
    """Import a GitHub project into the exegesis database. Returns True on
    success, False on failure.
    """
    url = 'https://api.github.com/repos/{}/{}/git/trees/{}?recursive=1'.format(
        username, repo, commit_hash)
    headers = {'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response = r.json()
        project = Project(name=(username + ':' + repo), source=Project.GITHUB)
        project.save()

        # Create the root directory.
        Directory.objects.create(project=project, fullpath='', dirpath='',
            name='')

        for entry in response['tree']:
            fullpath = entry['path']
            last_slash = fullpath.rfind('/')
            if last_slash != -1:
                dirpath = fullpath[:last_slash+1]
                name = fullpath[last_slash+1:]
            else:
                dirpath = ''
                name = fullpath

            if entry['type'] == 'tree':
                Directory.objects.create(project=project, fullpath=fullpath,
                    dirpath=dirpath, name=name)
            else:
                Snippet.objects.create(project=project, fullpath=fullpath,
                    dirpath=dirpath, name=name,
                    downloaded=False, download_source=entry['url'])
        return True
    else:
        return False
