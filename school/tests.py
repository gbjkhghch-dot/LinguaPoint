from django.test import TestCase
from django.urls import reverse
from .forms import ApplicationForm
class PagesTest(TestCase):
    def test_home(self):self.assertEqual(self.client.get(reverse('home')).status_code,200)
    def test_catalog(self):self.assertEqual(self.client.get(reverse('catalog')).status_code,200)
    def test_search(self):self.assertEqual(self.client.get(reverse('search')).status_code,200)
    def test_api(self):self.assertEqual(self.client.get(reverse('courses_api')).status_code,200)
    def test_account_requires_auth(self):self.assertEqual(self.client.get(reverse('account')).status_code,302)
    def test_form_rejects_bad_phone(self):
        form=ApplicationForm(data={'name':'Анна','phone':'123','email':'anna@example.com','level':'A1','consent':'on'})
        self.assertFalse(form.is_valid())


class RequirementCoverageTests(TestCase):
    def test_catalog_has_named_api_url(self):
        response = self.client.get(reverse('catalog'))
        self.assertContains(response, 'data-api-url="' + reverse('courses_api') + '"')

    def test_api_empty_list_shape(self):
        response = self.client.get(reverse('courses_api'), {'q': 'unmatched_course_query'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])
        self.assertEqual(response.json()['count'], 0)

    def test_catalog_page_has_page_heading(self):
        self.assertContains(self.client.get(reverse('catalog')), '<h1>Каталог курсов</h1>', html=True)

    def test_login_has_csrf(self):
        self.assertContains(self.client.get(reverse('login')), 'csrfmiddlewaretoken')

    def test_application_name_validation(self):
        form = ApplicationForm(data={'name':'1','phone':'+7 999 123-45-67','email':'anna@example.com','level':'A1','consent':'on'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
