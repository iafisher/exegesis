from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve
from . import models, views


class TestURLs(TestCase):
    """Test that URLs resolve to the expected views."""

    def test_can_resolve_index(self):
        found = resolve('/')
        self.assertEqual(found.func, views.index)

    def test_can_resolve_login(self):
        found = resolve('/login')
        self.assertEqual(found.func, views.login)

    def test_can_resolve_import(self):
        found = resolve('/import')
        self.assertEqual(found.func, views.import_project)

    def test_can_resolve_project_path(self):
        found = resolve('/project/python:cpython')
        self.assertEqual(found.func, views.path)

    def test_can_resolve_directory_path(self):
        found = resolve('/project/python:cpython/Python')
        self.assertEqual(found.func, views.path)

    def test_can_resolve_snippet_path(self):
        found = resolve('/project/python:cpython/LICENSE')
        self.assertEqual(found.func, views.path)


class TestPages(TestCase):
    """Test that the proper templates are used to render pages."""

    def setUp(self):
        User = get_user_model()
        User.objects.create_user('temporary', 'temporary@gmail.com', 'pwd')

    def test_index_page_template(self):
        self.client.login(username='temporary', password='pwd')
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'annotate/index.html')

    def test_login_page_template(self):
        response = self.client.get('/login')
        self.assertTemplateUsed(response, 'annotate/login.html')

    def test_path_page_template(self):
        self.client.login(username='temporary', password='pwd')

        # Create a minimal project with a directory and a file.
        project = models.Project.objects.create(name='temporary')
        models.Directory.objects.create(fullpath='', dirpath='', name='',
            project=project)
        models.Snippet.objects.create(fullpath='README.txt', dirpath='',
            name='README.txt', text='Lorem ipsum', project=project,
            downloaded=True)

        response = self.client.get('/project/temporary')
        self.assertTemplateUsed(response, 'annotate/directory.html')

        response = self.client.get('/project/temporary/README.txt')
        self.assertTemplateUsed(response, 'annotate/snippet.html')

    def test_login_page_redirects(self):
        self.client.login(username='temporary', password='pwd')
        response = self.client.get('/login')
        self.assertRedirects(response, '/')

    def test_index_page_redirects(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_logout_page_redirects(self):
        self.client.login(username='temporary', password='pwd')
        response = self.client.get('/logout')
        self.assertRedirects(response, '/login')

        # Can't access pages after logging out.
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')
