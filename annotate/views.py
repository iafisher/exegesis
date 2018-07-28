from django.shortcuts import get_object_or_404, render

from .models import Snippet


def index(request):
    snippets = Snippet.objects.all()
    return render(request, 'annotate/index.html', {'snippets': snippets})


def snippet(request, path):
    snip = get_object_or_404(Snippet, path=path)
    return render(request, 'annotate/snippet.html', {'snippet': snip})
