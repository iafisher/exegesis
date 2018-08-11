import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from annotate.models import Comment, Project, Snippet, get_from_path


@login_required
def update_comment(request):
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        projectname = obj['project']
        path = obj['path']
        text = obj['text']
        lineno = obj['lineno']

        project = get_object_or_404(Project, name=projectname)
        snippet = get_from_path(project, path)
        if not isinstance(snippet, Snippet):
            raise Http404('No Snippet matches the given query.')

        comment, _ = Comment.objects.get_or_create(
            user=request.user, lineno=lineno, snippet=snippet,
        )
        comment.text = text
        comment.save()
        return HttpResponse()
    else:
        return redirect('annotate:index')


@login_required
def delete_comment(request):
    if request.method == 'POST':
        obj = json.loads(request.body.decode('utf-8'))
        projectname = obj['project']
        path = obj['path']
        lineno = obj['lineno']

        project = get_object_or_404(Project, name=projectname)
        snippet = get_from_path(project, path)
        if not isinstance(snippet, Snippet):
            raise Http404('No Snippet matches the given query.')

        comment = Comment.objects.get(
            user=request.user, lineno=lineno, snippet=snippet,
        )
        comment.delete()
        return HttpResponse()
    else:
        return redirect('annotate:index')


@login_required
def fetch(request):
    projectname = request.GET.get('project')
    path = request.GET.get('path')

    if projectname is None or path is None:
        return HttpResponse(status=400)

    project = Project.objects.get(name=projectname)
    snippet = get_from_path(project, path)

    payload = {
        'comments': [c.to_json() for c in snippet.comment_set.all()],
    }
    return JsonResponse(payload)
