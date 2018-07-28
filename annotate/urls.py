from django.urls import path

from . import views

app_name = 'annotate'

urlpatterns = [
    path('', views.index, name='index'),
    path('snippet/<path>', views.snippet, name='snippet'),
]
