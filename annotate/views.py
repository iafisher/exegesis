import json

from django.shortcuts import get_object_or_404, render

from .models import Comment, Snippet


def index(request):
    snippets = Snippet.objects.all()
    return render(request, 'annotate/index.html', {'snippets': snippets})


def snippet(request, path):
    snip = get_object_or_404(Snippet, path=path)
    comments = Comment.objects.filter(snippet=snip)
    context = {
        'snippet': snip,
        'comments': json.dumps([c.to_json() for c in comments]),
    }
    return render(request, 'annotate/snippet.html', context)
