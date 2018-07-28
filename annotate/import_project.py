import base64

import requests

from .models import Project, ProjectFile


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
        project = Project(title='github:{}:{}'.format(username, repo))
        project.save()
        for entry in response['tree']:
            ftype = ProjectFile.DIRECTORY if entry['type'] == 'tree' else \
                    ProjectFile.REGULAR_FILE
            projectfile = ProjectFile(project=project, name=entry['path'],
                downloaded=False, download_source=entry['url'], filetype=ftype)
            projectfile.save()
        return True
    else:
        return False
