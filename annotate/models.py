from django.db import models
from django.urls import reverse


class Snippet(models.Model):
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    text = models.TextField()
    path = models.CharField(max_length=500, unique=True)

    def get_absolute_url(self):
        return reverse('annotate:snippet', kwargs={'path': self.path})

    def __str__(self):
        return self.path


class Comment(models.Model):
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    text = models.TextField()
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    lineno = models.IntegerField()

    def to_json(self):
        return {'text': self.text, 'lineno': self.lineno}

    def __str__(self):
        return 'Comment on {0.snippet}, line {0.lineno}'.format(self)


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
        return reverse('annotate:projectfile', kwargs=kwargs)

    def __str__(self):
        suffix = '/' if self.filetype == self.DIRECTORY else ''
        return self.name + suffix + ' (' + str(self.project) + ')'


class ProjectComment(models.Model):
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    text = models.TextField()
    projectfile = models.ForeignKey(ProjectFile, on_delete=models.CASCADE)
    lineno = models.IntegerField()

    def to_json(self):
        return {'text': self.text, 'lineno': self.lineno}

    def __str__(self):
        return 'Comment on {0.projectfile}, line {0.lineno}'.format(self)
