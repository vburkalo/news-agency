from datetime import timedelta

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from pulse.models import Topic, Redactor, Newspaper


class TopicModelTest(TestCase):
    def test_string_representation(self):
        topic = Topic(name="Politics")
        self.assertEqual(str(topic), topic.name)

    def test_topic_name_max_length(self):
        topic = Topic.objects.create(name="a" * 300)
        max_length = topic._meta.get_field("name").max_length
        self.assertEqual(max_length, 255)

    def test_name_is_unique(self):
        Topic.objects.create(name="UniqueName")
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="UniqueName")

    def test_blank_name(self):
        topic = Topic(name="")
        with self.assertRaises(ValidationError):
            if topic.full_clean():
                topic.save()

    def test_save_and_retrieve(self):
        topic = Topic.objects.create(name="Education")
        retrieved = Topic.objects.get(name="Education")
        self.assertEqual(retrieved.name, topic.name)

    def test_default_values(self):
        topic = Topic.objects.create(name="Default Topic")
        self.assertEqual(topic.name, "Default Topic")


class RedactorModelTest(TestCase):
    def test_string_representation(self):
        redactor = Redactor(username="john_doe", years_of_experience=5)
        redactor.save()
        self.assertEqual(str(redactor), "john_doe (5 years of experience)")

    def test_default_years_of_experience(self):
        redactor = Redactor(username="jane_doe")
        redactor.save()
        self.assertEqual(redactor.years_of_experience, 0)

    def test_negative_years_of_experience(self):
        redactor = Redactor(username="test_user", years_of_experience=-1)
        with self.assertRaises(ValidationError):
            if redactor.full_clean():
                redactor.save()

    def test_excessive_years_of_experience(self):
        redactor = Redactor(username="test_user", years_of_experience=100)
        with self.assertRaises(ValidationError):
            if redactor.full_clean():
                redactor.save()

    def test_multiple_redactor_creation(self):
        Redactor.objects.create(username="user1", years_of_experience=5)
        Redactor.objects.create(username="user2", years_of_experience=10)
        count = Redactor.objects.count()
        self.assertEqual(count, 2)

    def test_update_years_of_experience(self):
        redactor = Redactor.objects.create(
            username="update_test", years_of_experience=2
        )
        redactor.years_of_experience = 10
        redactor.save()
        updated_redactor = Redactor.objects.get(username="update_test")
        self.assertEqual(updated_redactor.years_of_experience, 10)

    def test_redactor_authentication(self):
        Redactor.objects.create_user(
            username="auth_user",
            password="testpass123"
        )
        user = authenticate(username="auth_user", password="testpass123")
        self.assertIsNotNone(user)


class NewspaperModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Science")
        self.redactor = Redactor.objects.create(
            username="editor", years_of_experience=10
        )
        self.newspaper = Newspaper.objects.create(
            title="Daily News",
            content="Some content here",
            published_date=timezone.now().date(),
        )
        self.newspaper.topic.add(self.topic)
        self.newspaper.publishers.add(self.redactor)

    def test_string_representation(self):
        self.assertEqual(str(self.newspaper), "Daily News")

    def test_newspaper_relationships(self):
        self.assertIn(self.topic, self.newspaper.topic.all())
        self.assertIn(self.redactor, self.newspaper.publishers.all())

    def test_fields(self):
        self.assertEqual(
            self.newspaper._meta.get_field("title").max_length, 255
        )
        self.assertIsInstance(
            self.newspaper.published_date, type(timezone.now().date())
        )

    def test_future_published_date(self):
        future_date = timezone.now().date() + timedelta(days=30)
        self.newspaper.published_date = future_date
        self.newspaper.save()
        self.assertEqual(self.newspaper.published_date, future_date)

    def test_past_published_date(self):
        past_date = timezone.now().date() - timedelta(days=365)
        self.newspaper.published_date = past_date
        self.newspaper.save()
        self.assertEqual(self.newspaper.published_date, past_date)

    def test_newspaper_search_by_title(self):
        search_result = Newspaper.objects.filter(title__icontains="Daily")
        self.assertIn(self.newspaper, search_result)

    def test_deletion_of_topic(self):
        self.topic.delete()
        self.assertNotIn(self.topic, self.newspaper.topic.all())

    def test_deletion_of_publisher(self):
        self.redactor.delete()
        self.assertNotIn(self.redactor, self.newspaper.publishers.all())

    def test_adding_multiple_publishers(self):
        another_redactor = Redactor.objects.create(
            username="coeditor", years_of_experience=5
        )
        self.newspaper.publishers.add(another_redactor)
        self.assertEqual(self.newspaper.publishers.count(), 2)
