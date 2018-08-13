from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.urls import reverse


class Project(models.Model):
    name = models.CharField(max_length=256, unique=True)
    imported = models.DateField(auto_now_add=True)

    GITHUB = 'GH'
    CUSTOM = 'CM'
    SOURCE_CHOICES = (
        (GITHUB, 'GitHub'),
        (CUSTOM, 'Custom'),
    )
    source = models.CharField(max_length=2, choices=SOURCE_CHOICES,
        default=CUSTOM)

    def get_absolute_url(self):
        kwargs = {'project': self.name}
        return reverse('annotate:project_index', kwargs=kwargs)

    def __str__(self):
        return self.name


class Directory(models.Model):
    fullpath = models.TextField(blank=True)
    dirpath = models.TextField(blank=True)
    name = models.CharField(max_length=256, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def get_absolute_url(self):
        if self.fullpath:
            kwargs = {'project': self.project.name, 'path': self.fullpath}
            return reverse('annotate:path', kwargs=kwargs)
        else:
            kwargs = {'project': self.project.name}
            return reverse('annotate:project_index', kwargs=kwargs)

    def __str__(self):
        if self.fullpath:
            return '{0.project}:{0.fullpath}'.format(self)
        else:
            return '{0.project}:/'.format(self)

    class Meta:
        verbose_name_plural = 'directories'


class Snippet(models.Model):
    fullpath = models.TextField()
    dirpath = models.TextField()
    name = models.CharField(max_length=256)
    text = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # If downloaded is False, then download_source contains the URL from which
    # the contents of the file can be downloaded.
    downloaded = models.BooleanField()
    download_source = models.URLField(blank=True)

    def get_absolute_url(self):
        kwargs = {'project': self.project.name, 'path': self.fullpath}
        return reverse('annotate:path', kwargs=kwargs)

    def __str__(self):
        return '{0.project}:{0.fullpath}'.format(self)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    text = models.TextField()
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    lineno = models.IntegerField()
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


def format_date(date):
    """Return a string in the form 'Tuesday 7 August 2018, 13:51 UTC'"""
    return date.strftime('%A ') + \
        date.strftime('%d %B %Y, %H:%M UTC').lstrip('0')
