from django.test import TestCase
from django.urls import resolve
from annotate import views


class TestURLs(TestCase):
    """Test that URLs resolve to the expected views."""

    def test_can_resolve_index(self):
        found = resolve('/')
        self.assertEqual(found.func, views.index)

    def test_can_resolve_login(self):
        found = resolve('/login')
        self.assertEqual(found.func, views.login)

    def test_can_resolve_logout(self):
        found = resolve('/logout')
        self.assertEqual(found.func, views.logout)

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
