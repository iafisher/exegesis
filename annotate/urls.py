from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),
    path('snippet/<path>', views.snippet, name='snippet'),
    path('snippet/<path>/update', views.update_comment, name='update'),
    path('snippet/<path>/delete', views.delete_comment, name='delete'),
    path('project/<title>', views.project, name='project'),
    path('project/<title>/<path:path>', views.projectfile_or_dir, name='projectfile'),
]
