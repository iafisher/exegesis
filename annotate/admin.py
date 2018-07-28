from django.contrib import admin

from .models import Snippet, Comment


admin.site.register(Snippet)
admin.site.register(Comment)
