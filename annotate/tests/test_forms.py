from django.test import TestCase
from annotate import forms


class TestForms(TestCase):
    def test_all_fields_required(self):
        form = forms.ImportProjectForm(data={'username': 'iafisher'})
        self.assertFalse(form.is_valid())
