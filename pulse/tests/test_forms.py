from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from pulse.forms import TopicForm, RedactorForm, NewspaperForm, NewspaperSearchForm
from pulse.models import Topic


class TopicFormTest(TestCase):
    def test_topic_form_valid(self):
        form = TopicForm(data={"name": "Test Topic"})
        self.assertTrue(form.is_valid())

    def test_topic_form_invalid(self):
        form = TopicForm(data={})
        self.assertFalse(form.is_valid())


class RedactorFormTest(TestCase):
    def test_redactor_form_valid(self):
        form_data = {
            "username": "testuser",
            "years_of_experience": 5,
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "ComplexPassword!2345",
            "password2": "ComplexPassword!2345",
        }
        form = RedactorForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_redactor_form_invalid(self):
        form_data = {
            "username": "",
            "years_of_experience": 5,
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "password123",
            "password2": "password123",
        }
        form = RedactorForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_redactor_form_invalid_email(self):
        form_data = {
            "username": "testuser",
            "years_of_experience": 5,
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email",
            "password1": "ComplexPassword!2345",
            "password2": "ComplexPassword!2345",
        }
        form = RedactorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class NewspaperFormTest(TestCase):
    def test_newspaper_form_valid(self):
        topic = Topic.objects.create(name="Test Topic")
        publisher = get_user_model().objects.create(username="test_publisher")
        form_data = {
            "title": "Test Newspaper",
            "content": "Test content",
            "published_date": date.today(),
            "topic": [topic.pk],
            "publishers": [publisher.pk],
        }
        form = NewspaperForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_newspaper_form_invalid(self):
        form = NewspaperForm(data={})
        self.assertFalse(form.is_valid())


class NewspaperSearchFormTest(TestCase):
    def test_newspaper_search_form_valid(self):
        form = NewspaperSearchForm(data={"title": "Test", "content": "Content"})
        self.assertTrue(form.is_valid())

    def test_newspaper_search_form_invalid(self):
        form = NewspaperSearchForm(data={})
        self.assertTrue(form.is_valid())
