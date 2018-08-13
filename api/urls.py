from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('<project>/<path:path>/update_comment', views.update_comment,
        name='update_comment2'),
    path('<project>/<path:path>/delete_comment', views.delete_comment,
        name='delete_comment2'),
    path('<project>/<path:path>/fetch', views.fetch, name='fetch2'),
    #path('import_project', views.import_project, name='import_project'),
]
