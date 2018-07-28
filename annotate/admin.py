from django.contrib import admin

from .models import Comment, Project, ProjectFile, Snippet


admin.site.register(Comment)
admin.site.register(Project)
admin.site.register(ProjectFile)
admin.site.register(Snippet)
