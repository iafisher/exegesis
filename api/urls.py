from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('update', views.update_comment, name='update_comment'),
    path('delete', views.delete_comment, name='delete_comment'),
    path('fetch', views.fetch, name='fetch'),
]
