from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse

from .forms import ApplicationForm
from .models import (
    Language,
    Level,
    StudentProfile,
    StudyGroup,
    CourseApplication,
)


class PagesTest(TestCase):

    def test_home(self):
        self.assertEqual(
            self.client.get(reverse('home')).status_code, 200
        )

    def test_catalog(self):
        self.assertEqual(
            self.client.get(reverse('catalog')).status_code, 200
        )

    def test_search(self):
        self.assertEqual(
            self.client.get(reverse('search')).status_code, 200
        )

    def test_api(self):
        self.assertEqual(
            self.client.get(reverse('courses_api')).status_code, 200
        )

    def test_account_requires_auth(self):
        self.assertEqual(
            self.client.get(reverse('account')).status_code, 302
        )

    def test_form_rejects_bad_phone(self):
        form = ApplicationForm(data={
            'name': 'Анна',
            'phone': '123',
            'email': 'anna@example.com',
            'level': 'A1',
            'consent': 'on'
        })

        self.assertFalse(form.is_valid())


class RequirementCoverageTests(TestCase):

    def test_catalog_has_named_api_url(self):
        response = self.client.get(reverse('catalog'))

        self.assertContains(
            response,
            'data-api-url="' + reverse('courses_api') + '"'
        )

    def test_api_empty_list_shape(self):
        response = self.client.get(
            reverse('courses_api'),
            {'q': 'unmatched_course_query'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])
        self.assertEqual(response.json()['count'], 0)

    def test_catalog_page_has_page_heading(self):
        self.assertContains(
            self.client.get(reverse('catalog')),
            '<h1>Каталог курсов</h1>',
            html=True
        )

    def test_login_has_csrf(self):
        self.assertContains(
            self.client.get(reverse('login')),
            'csrfmiddlewaretoken'
        )

    def test_application_name_validation(self):
        form = ApplicationForm(data={
            'name': '1',
            'phone': '+7 999 123-45-67',
            'email': 'anna@example.com',
            'level': 'A1',
            'consent': 'on'
        })

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


# Занятие 16. Негативные тесты

class ExceptionHandlingTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.owner = User.objects.create_user(
            username='test_owner',
            password='TestPassword123!'
        )

        cls.other_user = User.objects.create_user(
            username='test_other',
            password='TestPassword123!'
        )

        teacher_user = User.objects.create_user(
            username='test_teacher',
            password='TestPassword123!'
        )

        teacher, _ = StudentProfile.objects.get_or_create(
            user=teacher_user,
            defaults={
                'full_name': 'Тестовый преподаватель',
                'role': 'teacher'
            }
        )

        language = Language.objects.create(
            name='Английский',
            code='en'
        )

        level = Level.objects.create(
            language=language,
            code='A1',
            rank=1
        )

        cls.group = StudyGroup.objects.create(
            title='Тестовая группа A1',
            language=language,
            level=level,
            teacher=teacher,
            capacity=8,
            start_date=date(2026, 12, 15)
        )

    def valid_data(self):
        return {
            'name': 'Иван Иванов',
            'phone': '+79991234567',
            'email': 'ivan@example.com',
            'level': 'A1',
            'consent': 'on'
        }

    # NEG-01. Несуществующая запись

    def test_missing_course_returns_404(self):
        response = self.client.get(
            reverse('course', kwargs={'pk': 999999})
        )

        self.assertEqual(response.status_code, 404)

    # NEG-02. Доступ к чужой заявке

    def test_forbidden_application_returns_403(self):

        application = CourseApplication.objects.create(
            group=self.group,
            user=self.owner,
            name='Иван Иванов',
            phone='+79991234567',
            email='ivan@example.com',
            level='A1',
            consent=True
        )

        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                'application_success',
                kwargs={'pk': application.pk}
            )
        )

        self.assertEqual(response.status_code, 403)

    # NEG-03. Некорректная форма не создаёт запись

    def test_invalid_form_does_not_create_application(self):

        before = CourseApplication.objects.count()

        data = self.valid_data()
        data['phone'] = '123'

        response = self.client.post(
            reverse('apply', kwargs={'pk': self.group.pk}),
            data
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            CourseApplication.objects.count(),
            before
        )

        self.assertContains(
            response,
            'Укажите телефон: от 10 до 15 цифр.'
        )

    # NEG-04. Откат транзакции при ошибке

    def test_database_error_rolls_back_application(self):

        before = CourseApplication.objects.count()

        original_save = CourseApplication.save

        def save_then_fail(instance, *args, **kwargs):
            original_save(instance, *args, **kwargs)
            raise DatabaseError('Тестовая ошибка сохранения')

        with patch.object(
            CourseApplication,
            'save',
            save_then_fail
        ):
            with self.assertLogs(
                'school.views',
                level='ERROR'
            ):
                response = self.client.post(
                    reverse(
                        'apply',
                        kwargs={'pk': self.group.pk}
                    ),
                    self.valid_data()
                )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            CourseApplication.objects.count(),
            before
        )

        self.assertIn(
            'Не удалось сохранить заявку. Попробуйте позже.',
            response.context['form'].non_field_errors()
        )

    # NEG-05. Расчёт на пустой выборке

    def test_empty_queryset_calculation(self):

        response = self.client.get(
            reverse('courses_api'),
            {'q': 'nonexistent_course_999999'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)
        self.assertEqual(response.json()['results'], [])