from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),
    path('success', views.index, {'success': True}, name='success'),
    path('failure', views.index, {'success': False}, name='failure'),

    path('project/<name>', views.project_index, name='project_index'),
    path('project/<name>/<path:path>', views.path, name='path'),

    path('import', views.import_project, name='import_project'),

    path('login', views.login, name='login'),
    path('login/', views.login),
    path('logout', views.logout, name='logout'),
]
