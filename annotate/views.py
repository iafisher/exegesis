import json
from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .import_project import download_from_github, import_from_github
from .forms import ImportProjectForm
from .models import Comment, Project, ProjectFile


def index(request, success=None):
    projects = Project.objects.all()

    # Calculate the number of comments on each project.
    comment_count = defaultdict(int)
    for comment in Comment.objects.all():
        comment_count[comment.projectfile.project.title] += 1

    for project in projects:
        project.comment_count = comment_count[project.title]

    context = {
        'projects': projects,
        'form': ImportProjectForm(),
        'success': success,
    }
    return render(request, 'annotate/index.html', context)


def project(request, title):
    proj = get_object_or_404(Project, title=title)
    eligible = [f for f in proj.projectfile_set.order_by('name')
        if '/' not in f.name[:-1]]
    directories = [f for f in eligible if f.filetype == ProjectFile.DIRECTORY]
    files = [f for f in eligible if f.filetype == ProjectFile.REGULAR_FILE]
    context = {
        'project': proj,
        'directories': directories,
        'files': files,
    }
    return render(request, 'annotate/projectdir.html', context)


def projectfile_or_dir(request, title, path):
    proj = get_object_or_404(Project, title=title)
    pfile = get_object_or_404(ProjectFile, project=proj, name=path)
    if pfile.filetype == ProjectFile.DIRECTORY:
        return projectdir(request, proj, pfile)
    else:
        return projectfile(request, proj, pfile)


def projectdir(request, proj, pfile):
    eligible = proj.projectfile_set.filter(name__startswith=pfile.name + '/')
    directories = [f for f in eligible if f.filetype == ProjectFile.DIRECTORY]
    files = [f for f in eligible if f.filetype == ProjectFile.REGULAR_FILE]
    context = {
        'project': proj,
        'dir': pfile,
        'directories': directories,
        'files': files,
    }
    return render(request, 'annotate/projectdir.html', context)


def projectfile(request, proj, pfile):
    if not pfile.downloaded:
        contents = download_from_github(pfile.download_source)
        if contents:
            pfile.text = contents
            pfile.downloaded = True
            pfile.save()

    comments = Comment.objects.filter(projectfile=pfile)
    context = {
        'file': pfile,
        'comments_json': json.dumps([c.to_json() for c in comments]),
        'path_json': json.dumps(pfile.get_absolute_url()),
    }
    return render(request, 'annotate/projectfile.html', context)


def update_comment(request, title, path):
    proj = get_object_or_404(Project, title=title)
    pfile = get_object_or_404(ProjectFile, project=proj, name=path)
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        text = obj['text']
        lineno = obj['lineno']
        comment, _ = Comment.objects.get_or_create(
            lineno=lineno, projectfile=pfile
        )
        comment.text = text
        comment.save()
        return HttpResponse()
    else:
        return redirect('annotate:projectfile', title=title, path=path)


def delete_comment(request, title, path):
    proj = get_object_or_404(Project, title=title)
    pfile = get_object_or_404(ProjectFile, project=proj, name=path)
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        lineno = obj['lineno']
        comment = get_object_or_404(Comment, lineno=lineno,
            projectfile=pfile)
        comment.delete()
        return HttpResponse()
    else:
        return redirect('annotate:projectfile', title=title, path=path)


def import_project(request):
    if request.method == 'POST':
        form = ImportProjectForm(request.POST)
        if form.is_valid():
            import_from_github(form.cleaned_data['username'],
                form.cleaned_data['reponame'], form.cleaned_data['sha'])
            return redirect('annotate:success')
        else:
            return redirect('annotate:failure')
    else:
        return redirect('annotate:index')
