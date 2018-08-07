from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Project(models.Model):
    imported = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse('annotate:project', kwargs={'title': self.title})

    def __str__(self):
        return self.title


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    text = models.TextField(blank=True)

    # If downloaded is False, then download_source contains the URL from which
    # the contents of the file can be downloaded.
    downloaded = models.BooleanField()
    download_source = models.URLField(blank=True)

    REGULAR_FILE = 'f'
    DIRECTORY = 'd'
    FILETYPE_CHOICES = (
        (REGULAR_FILE, 'file'),
        (DIRECTORY, 'directory'),
    )
    filetype = models.CharField(max_length=1, choices=FILETYPE_CHOICES,
        default=REGULAR_FILE)

    def get_absolute_url(self):
        kwargs = {
            'title': self.project.title,
            'path': self.name,
        }
        return reverse('annotate:path', kwargs=kwargs)

    def __str__(self):
        suffix = '/' if self.filetype == self.DIRECTORY else ''
        return str(self.project) + '/' + self.name + suffix


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    text = models.TextField()
    projectfile = models.ForeignKey(ProjectFile, on_delete=models.CASCADE)
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
        return 'Comment on {0.projectfile}, line {0.lineno}'.format(self)


def format_date(date):
    """Return a string in the form 'Tuesday 7 August 2018, 13:51 UTC'"""
    return date.strftime('%A ') + \
        date.strftime('%d %B %Y, %H:%M UTC').lstrip('0')
