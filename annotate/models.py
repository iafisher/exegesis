from django.db import models
from django.urls import reverse


class Snippet(models.Model):
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
