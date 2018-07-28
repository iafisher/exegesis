import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Project, ProjectComment, ProjectFile, Snippet


def index(request):
    snippets = Snippet.objects.all()
    return render(request, 'annotate/index.html', {'snippets': snippets})


def snippet(request, path):
    snip = get_object_or_404(Snippet, path=path)
    comments = Comment.objects.filter(snippet=snip)
    context = {
        'snippet': snip,
        'comments_json': json.dumps([c.to_json() for c in comments]),
        'path_json': json.dumps(snip.path),
    }
    return render(request, 'annotate/snippet.html', context)


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
    return render(request, 'annotate/project.html', context)


def projectfile_or_dir(request, title, path):
    proj = get_object_or_404(Project, title=title)
    projfile = get_object_or_404(ProjectFile, project=proj, name=path)
    if projfile.filetype == ProjectFile.DIRECTORY:
        return projectdir(request, proj, projfile)
    else:
        return projectfile(request, proj, projfile)


def projectdir(request, proj, projfile):
    eligible = proj.projectfile_set.filter(name__startswith=projfile.name + '/')
    directories = [f for f in eligible if f.filetype == ProjectFile.DIRECTORY]
    files = [f for f in eligible if f.filetype == ProjectFile.REGULAR_FILE]
    context = {
        'project': proj,
        'dir': projfile,
        'directories': directories,
        'files': files,
    }
    return render(request, 'annotate/projectdir.html', context)


def projectfile(request, proj, projfile):
    comments = ProjectComment.objects.filter(projectfile=projfile)
    context = {
        'file': projfile,
        'comments_json': json.dumps([c.to_json() for c in comments]),
        'path_json': json.dumps(projfile.name),
    }
    return render(request, 'annotate/projectfile.html', context)


def update_comment(request, path):
    snip = get_object_or_404(Snippet, path=path)
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        text = obj['text']
        lineno = obj['lineno']
        comment, _ = Comment.objects.get_or_create(
            lineno=lineno, snippet=snip
        )
        comment.text = text
        comment.save()
        return HttpResponse()
    else:
        return redirect('annotate:snippet', path=path)


def delete_comment(request, path):
    snip = get_object_or_404(Snippet, path=path)
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        lineno = obj['lineno']
        comment = get_object_or_404(Comment, lineno=lineno, snippet=snip)
        comment.delete()
        return HttpResponse()
    else:
        return redirect('annotate:snippet', path=path)
