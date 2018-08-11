import json
from collections import defaultdict

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .import_project import download_from_github, import_from_github
from .forms import CreateProjectForm, CreateSnippetForm, ImportProjectForm
from .models import Comment, Directory, Project, Snippet, get_from_path


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
        'create_form': CreateProjectForm(),
        'import_form': ImportProjectForm(),
        'projects': projects,
    }
    return render(request, 'annotate/index.html', context)


@login_required
def project_index(request, name):
    project = get_object_or_404(Project, name=name)
    directories = project.directory_set.filter(project=project, parent=None) \
        .order_by('name')
    snippets = project.snippet_set.filter(project=project, parent=None) \
        .order_by('name')
    context = {
        'project': project,
        'directories': directories,
        'form': CreateSnippetForm(),
        'snippets': snippets,
    }
    return render(request, 'annotate/directory.html', context)


@login_required
def path(request, name, path):
    project = get_object_or_404(Project, name=name)
    snippet_or_directory = get_from_path(project, path)
    if isinstance(snippet_or_directory, Snippet):
        return snippet_index_core(request, project, snippet_or_directory)
    else:
        return directory_index_core(request, project, snippet_or_directory)


def directory_index_core(request, project, directory):
    directories = Directory.objects.filter(project=project, parent=directory)
    snippets = Snippet.objects.filter(project=project, parent=directory)
    context = {
        'project': project,
        'dir': directory,
        'directories': directories,
        'form': CreateSnippetForm(),
        'snippets': snippets,
    }
    return render(request, 'annotate/directory.html', context)


@login_required
def snippet_index_core(request, project, snippet):
    if not snippet.downloaded and snippet.project.source == Project.GITHUB:
        contents = download_from_github(snippet.download_source)
        if contents:
            snippet.text = contents
            snippet.downloaded = True
            snippet.save()

    comments = Comment.objects.filter(snippet=snippet)
    context = {
        'comments_json': json.dumps([c.to_json() for c in comments]),
        'path_json': json.dumps(snippet.get_path()),
        'project_json': json.dumps(project.name),
        'snippet': snippet,
    }
    return render(request, 'annotate/snippet.html', context)


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
                return redirect('annotate:failure')
            else:
                messages.success(request, 'Project imported successfully.')
                return redirect('annotate:index')
        else:
            messages.error(request, 'Failed to import project.')
            return redirect('annotate:failure')
    else:
        return redirect('annotate:index')


@login_required
def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['projectname']
            try:
                Project.objects.create(name=name, source=Project.CUSTOM)
            except:
                messages.error(request, 'Failed to create project.')
                return redirect('annotate:index')
            else:
                messages.success(request, 'Project created successfully.')
                return redirect('annotate:index')
        else:
            messages.error(request, 'Failed to create project.')
            return redirect('annotate:failure')
    else:
        return redirect('annotate:index')


@login_required
def create_snippet(request):
    if request.method == 'POST':
        form = CreateSnippetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['projectname']
            try:
                Snippet.objects.create
            except:
                messages.error(request, 'Failed to create snippet.')
                return redirect('annotate:index')
            else:
                messages.success(request, 'Snippet created successfully.')
                return redirect('annotate:index')
        else:
            messages.error(request, 'Failed to create snippet.')
            return redirect('annotate:failure')
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
            context = {
                'form': blank_form,
                'errormsg': 'Invalid username or password',
            }
            return render(request, 'annotate/login.html', context)
    else:
        form = AuthenticationForm()
        context = {
            'form': form,
            'next': request.GET.get('next')
        }
        return render(request, 'annotate/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('annotate:login')
