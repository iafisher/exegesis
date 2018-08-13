import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from annotate.models import Comment, Project, Snippet


@login_required
def update_comment(request, project, path):
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        text = obj['text']
        lineno = obj['lineno']

        project = get_object_or_404(Project, name=project)
        snippet = get_object_or_404(Snippet, project=project, fullpath=path)

        comment, _ = Comment.objects.get_or_create(
            user=request.user, lineno=lineno, snippet=snippet,
        )
        comment.text = text
        comment.save()

        return HttpResponse()
    else:
        return redirect('annotate:path', projectname, path)


@login_required
def delete_comment(request, project, path):
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        lineno = obj['lineno']

        project = get_object_or_404(Project, name=project)
        snippet = get_object_or_404(Snippet, project=project, fullpath=path)

        comment = Comment.objects.get(
            user=request.user, lineno=lineno, snippet=snippet,
        )
        comment.delete()

        return HttpResponse()
    else:
        return redirect('annotate:path', projectname, path)


@login_required
def fetch(request, project, path):
    project = Project.objects.get(name=project)
    snippet = get_object_or_404(Snippet, project=project, fullpath=path)
    payload = {
        'comments': [c.to_json() for c in snippet.comment_set.all()],
        'text': snippet.text,
    }
    return JsonResponse(payload)
