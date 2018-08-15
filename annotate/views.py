import json
from collections import defaultdict

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .import_project import download_from_github, import_from_github
from .forms import ImportProjectForm
from .models import Comment, Directory, Project, Snippet


@login_required
def index(request):
    projects = Project.objects.all()

    # Calculate the number of comments on each project.
    comment_count = defaultdict(int)
    for comment in Comment.objects.all():
        comment_count[comment.snippet.project.name] += 1

    for project in projects:
        project.comment_count = comment_count[project.name]

    context = {
        'import_form': ImportProjectForm(),
        'projects': projects,
    }
    return render(request, 'annotate/index.html', context)


@login_required
def path(request, project, path=''):
    project = get_object_or_404(Project, name=project)
    try:
        snippet = Snippet.objects.get(project=project, fullpath=path)
    except Snippet.DoesNotExist:
        directory = get_object_or_404(Directory, project=project, fullpath=path)
        return directory_index_core(request, directory)
    else:
        return snippet_index_core(request, snippet)


def directory_index_core(request, directory):
    path = directory.fullpath + '/' if directory.fullpath else ''
    project = directory.project

    directories = Directory.objects.filter(project=project,
        dirpath=path).exclude(fullpath='').order_by('name')
    snippets = Snippet.objects.filter(project=project, dirpath=path) \
        .order_by('name')

    context = {
        'project': project,
        'dir': directory,
        'directories': directories,
        'snippets': snippets,
    }
    return render(request, 'annotate/directory.html', context)


def snippet_index_core(request, snippet):
    if not snippet.downloaded and snippet.project.source == Project.GITHUB:
        contents = download_from_github(snippet.download_source)
        if contents:
            snippet.text = contents
            snippet.downloaded = True
            snippet.save()
    return render(request, 'annotate/snippet.html', {'snippet': snippet})


@login_required
def import_project(request):
    if request.method == 'POST':
        form = ImportProjectForm(request.POST)
        if form.is_valid():
            try:
                import_from_github(form.cleaned_data['username'],
                    form.cleaned_data['reponame'], form.cleaned_data['sha'])
            except:
                messages.error(request, 'Failed to import project.')
                return redirect('annotate:index')
            else:
                messages.success(request, 'Project imported successfully.')
                return redirect('annotate:index')
        else:
            messages.error(request, 'Failed to import project.')
            return redirect('annotate:index')
    else:
        return redirect('annotate:index')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(request.POST['next'] or '/')
        else:
            blank_form = AuthenticationForm()
            messages.error(request, 'Invalid username or password')
            return render(request, 'annotate/login.html', {'form': blank_form})
    else:
        if request.user.is_authenticated:
            return redirect('/')

        form = AuthenticationForm()
        context = {
            'form': form,
            'next': request.GET.get('next')
        }
        return render(request, 'annotate/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('annotate:login')
