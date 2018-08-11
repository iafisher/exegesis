from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.urls import reverse


class Project(models.Model):
    name = models.CharField(max_length=256)
    imported = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('annotate:project_index', kwargs={'name': self.name})

    def __str__(self):
        return self.name


class Directory(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey('Directory', on_delete=models.CASCADE,
        null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + '/' + self.name
        else:
            return self.project.get_absolute_url() + '/' + self.name

    def get_path(self):
        if self.parent:
            return self.parent.get_path() + '/' + self.name
        else:
            return self.name

    def parent_chain(self):
        parents = []
        me = self
        while me.parent:
            parents.append(me.parent)
            me = me.parent
        parents.reverse()
        return parents

    def __str__(self):
        if self.parent:
            return '{0.parent}{0.name}/'.format(self)
        else:
            return '{0.project}:{0.name}/'.format(self)

    class Meta:
        verbose_name_plural = 'directories'


class Snippet(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField(blank=True)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True,
        blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # If downloaded is False, then download_source contains the URL from which
    # the contents of the file can be downloaded.
    downloaded = models.BooleanField()
    download_source = models.URLField(blank=True)

    def parent_chain(self):
        parents = []
        me = self
        while me.parent:
            parents.append(me.parent)
            me = me.parent
        parents.reverse()
        return parents

    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + '/' + self.name
        else:
            return self.project.get_absolute_url() + '/' + self.name

    def get_path(self):
        if self.parent:
            return self.parent.get_path() + '/' + self.name
        else:
            return self.name

    def __str__(self):
        if self.parent:
            return '{0.parent}{0.name}'.format(self)
        else:
            return '{0.project}:{0.name}'.format(self)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    text = models.TextField()
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    lineno = models.IntegerField()
    parent = models.ForeignKey('Comment', blank=True, null=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_json(self):
        return {
            'created': format_date(self.created),
            'last_updated': format_date(self.last_updated),
            'lineno': self.lineno,
            'text': self.text,
            'user': self.user.username,
        }

    def __str__(self):
        return 'Comment on {0.snippet}, line {0.lineno}'.format(self)


def get_from_path(project, path):
    *path_components, pathentry = path.split('/')
    parent = None
    for component in path_components:
        try:
            parent = Directory.objects.get(project=project, parent=parent,
                name=component)
        except Directory.DoesNotExist:
            raise Http404('No Directory matches the given query.')
    try:
        return Snippet.objects.get(project=project, parent=parent,
            name=pathentry)
    except Snippet.DoesNotExist:
        try:
            return Directory.objects.get(project=project, parent=parent,
                name=pathentry)
        except Directory.DoesNotExist:
            raise Http404('No Directory matches the given query.')


def format_date(date):
    """Return a string in the form 'Tuesday 7 August 2018, 13:51 UTC'"""
    return date.strftime('%A ') + \
        date.strftime('%d %B %Y, %H:%M UTC').lstrip('0')
