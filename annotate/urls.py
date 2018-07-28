from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),
    path('success', views.index, {'success': True}, name='success'),
    path('failure', views.index, {'success': False}, name='failure'),

    path('project/<title>/<path:path>/update', views.update_comment,
        name='update'),
    path('project/<title>/<path:path>/delete', views.delete_comment,
        name='delete'),

    path('project/<title>', views.project, name='project'),
    path('project/<title>/<path:path>', views.projectfile_or_dir,
        name='projectfile'),

    path('import', views.import_project, name='import_project'),
]
