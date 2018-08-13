from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),

    path('project/<project>', views.path, name='project_index'),
    path('project/<project>/<path:path>', views.path, name='path'),

    path('import', views.import_project, name='import_project'),

    path('login', views.login, name='login'),
    path('login/', views.login),
    path('logout', views.logout, name='logout'),
]
