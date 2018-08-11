from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),

    path('project/<name>', views.project_index, name='project_index'),
    path('project/<name>/<path:path>', views.path, name='path'),

    path('import', views.import_project, name='import_project'),
    path('create', views.create_project, name='create_project'),

    path('login', views.login, name='login'),
    path('login/', views.login),
    path('logout', views.logout, name='logout'),
]
