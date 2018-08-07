from django.contrib import admin

from .models import Comment, Directory, Project, Snippet


admin.site.register(Comment)
admin.site.register(Directory)
admin.site.register(Project)
admin.site.register(Snippet)
