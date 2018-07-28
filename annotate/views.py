import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Snippet


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
