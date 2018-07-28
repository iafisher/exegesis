from django.db import models


class Snippet(models.Model):
    text = models.TextField()
    path = models.CharField(max_length=500)


class Comment(models.Model):
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    text = models.TextField()
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
