import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Project, ProjectFile


def index(request):
    projects = Project.objects.all()
    return render(request, 'annotate/index.html', {'projects': projects})


def project(request, title):
    proj = get_object_or_404(Project, title=title)
    directories = [f for f in proj.projectfile_set.order_by('name')
        if f.filetype == ProjectFile.DIRECTORY]
    files = [f for f in proj.projectfile_set.order_by('name')
        if f.filetype == ProjectFile.REGULAR_FILE]
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
