from django.contrib.auth import get_user_model
from django.test import TestCase
from annotate import models


class TestPages(TestCase):
    """Test that the proper templates are used to render pages."""

    def setUp(self):
        User = get_user_model()
        User.objects.create_user('temporary', 'temporary@example.com', 'pwd')

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
