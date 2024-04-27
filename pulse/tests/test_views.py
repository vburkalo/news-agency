from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from pulse.models import Topic, Redactor, Newspaper


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(name="Science")
        Redactor.objects.create(username="editor", password="password123")
        Newspaper.objects.create(
            title="Daily News",
            content="Content here",
            published_date="2020-01-01"
        )

    def test_index_view_status_code(self):
        response = self.client.get(reverse("pulse:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        response = self.client.get(reverse("pulse:index"))
        self.assertTemplateUsed(response, "pulse/index.html")

    def test_index_view_context_data(self):
        response = self.client.get(reverse("pulse:index"))
        self.assertEqual(response.context["num_topics"], Topic.objects.count())
        self.assertEqual(response.context["num_redactors"],
                         Redactor.objects.count())
        self.assertEqual(response.context["num_newspapers"],
                         Newspaper.objects.count())

    def test_index_view_no_records(self):
        Topic.objects.all().delete()
        Redactor.objects.all().delete()
        Newspaper.objects.all().delete()
        response = self.client.get(reverse("pulse:index"))
        self.assertEqual(response.context["num_topics"], 0)
        self.assertEqual(response.context["num_redactors"], 0)
        self.assertEqual(response.context["num_newspapers"], 0)


class TopicListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_topics = 15
        for topic_id in range(number_of_topics):
            Topic.objects.create(name=f"Topic {topic_id}")

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/pulse/topics/")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("pulse:topics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pulse/topic_list.html")

    def test_context_data(self):
        response = self.client.get(reverse("pulse:topics"))
        self.assertTrue("topic_list" in response.context)
        self.assertEqual(len(response.context["topic_list"]), 5)

    def test_pagination_is_correct(self):
        response = self.client.get(reverse("pulse:topics"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["topic_list"]), 5)

    def test_redirection_for_unauthenticated_users(self):
        self.client.logout()
        response = self.client.get(reverse("pulse:topics"))
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(response.status_code, 302)
        self.assertTrue("/accounts/login/" in response.url)

    def test_view_allows_only_get_method(self):
        response = self.client.post(reverse("pulse:topics"))
        self.assertEqual(response.status_code, 405)

    def test_view_sorts_topics_correctly(self):
        response = self.client.get(reverse("pulse:topics") + "?sort=name")
        topics = response.context["topic_list"]
        self.assertEqual(topics[0].name, "Topic 0")

    def test_sql_injection_security(self):
        response = self.client.get(
            reverse("pulse:topics"), {"name": "1'; DROP TABLE topics; --"}
        )
        self.assertNotIn("DROP TABLE", response.content.decode())


class TopicCRUDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )

    def setUp(self):
        self.client.login(username="testuser", password="12345")

    def test_create_topic(self):
        response = self.client.post(
            reverse("pulse:topic-create"), {"name": "New Topic"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Topic.objects.filter(name="New Topic").exists())

    def test_update_topic(self):
        topic = Topic.objects.create(name="Old Topic")
        response = self.client.post(
            reverse(
                "pulse:topic-update",
                args=[topic.id]),
            {"name": "Updated Topic"}
        )
        self.assertEqual(response.status_code, 302)
        topic.refresh_from_db()
        self.assertEqual(topic.name, "Updated Topic")

    def test_delete_topic(self):
        topic = Topic.objects.create(name="Delete Topic")
        response = self.client.post(
            reverse("pulse:topic-delete", args=[topic.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Topic.objects.filter(name="Delete Topic").exists())

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse("pulse:topic-create"))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/accounts/login/" in response.url)


class RedactorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_redactors = 10
        for redactor_id in range(number_of_redactors):
            Redactor.objects.create(
                username=f"user{redactor_id}",
                password="12345")

    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("pulse:redactors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("pulse:redactors"))
        self.assertTemplateUsed(response, "pulse/redactor_list.html")

    def test_pagination_is_correct(self):
        response = self.client.get(reverse("pulse:redactors"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])

    def test_pagination_second_page(self):
        # Test the second page of pagination
        response = self.client.get(reverse("pulse:redactors") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        # Assuming the second page should have the remaining 5 redactors
        self.assertEqual(len(response.context["redactors"]), 5)


class RedactorDetailViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")
        self.redactor = Redactor.objects.create(
            username="detailuser",
            password="12345"
        )

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse("pulse:redactor-detail", args=[self.redactor.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse("pulse:redactor-detail", args=[self.redactor.id])
        )
        self.assertTemplateUsed(response, "pulse/redactor_detail.html")


class RedactorCreateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_create_redactor(self):
        post_data = {
            "username": "newuser",
            "password1": "newpass123",
            "password2": "newpass123",
            "years_of_experience": 5,
        }
        response = self.client.post(
            reverse("pulse:redactor-create"),
            post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Redactor.objects.filter(username="newuser").exists())


class RedactorUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")
        self.redactor = Redactor.objects.create(
            username="updateuser",
            email="update@example.com",
            password="12345",
            years_of_experience=2,
        )

    def test_update_redactor(self):
        post_data = {
            "username": "updateuser",
            "email": "update@example.com",
            "years_of_experience": 10,
            "password1": "newpass123",
            "password2": "newpass123",
        }
        response = self.client.post(
            reverse(
                "pulse:redactor-update",
                args=[self.redactor.id]), post_data
        )
        if response.status_code != 302:
            print(response.context["form"].errors)
        self.assertEqual(response.status_code, 302)
        self.redactor.refresh_from_db()
        self.assertEqual(self.redactor.years_of_experience, 10)


class RedactorDeleteViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")
        self.redactor = Redactor.objects.create(
            username="deleteuser",
            password="12345"
        )

    def test_delete_redactor(self):
        response = self.client.post(
            reverse("pulse:redactor-delete", args=[self.redactor.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Redactor.objects.filter(
            username="deleteuser").exists()
                         )


class NewspaperListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(10):
            Newspaper.objects.create(
                title=f"Newspaper {i}",
                content="Content",
                published_date="2020-01-01"
            )

    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse("pulse:newspapers"))
        self.assertEqual(response.status_code, 200)

    def test_pagination_is_correct(self):
        response = self.client.get(reverse("pulse:newspapers"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["newspaper_list"]), 5)

    def test_search_functionality(self):
        response = self.client.get(
            reverse("pulse:newspapers") + "?title=Newspaper 0"
        )
        self.assertEqual(len(response.context["newspaper_list"]), 1)


class NewspaperDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.newspaper = Newspaper.objects.create(
            title="Detailed View Newspaper",
            content="Detailed content",
            published_date="2020-01-01",
        )

    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse("pulse:newspaper-detail", args=[self.newspaper.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse("pulse:newspaper-detail", args=[self.newspaper.pk])
        )
        self.assertTemplateUsed(response, "pulse/newspaper_detail.html")

    def test_context_data(self):
        response = self.client.get(
            reverse("pulse:newspaper-detail", args=[self.newspaper.pk])
        )
        self.assertEqual(response.context["newspaper"].pk, self.newspaper.pk)


class NewspaperCreateViewTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_create_newspaper(self):
        response = self.client.post(
            reverse("pulse:newspaper-create"),
            {
                "title": "New Newspaper",
                "content": "Content of new newspaper",
                "published_date": "2022-01-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Newspaper.objects.filter(
            title="New Newspaper").exists()
                        )


class NewspaperUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.newspaper = Newspaper.objects.create(
            title="Original Title",
            content="Original Content",
            published_date="2020-01-01",
        )

    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_update_newspaper(self):
        response = self.client.post(
            reverse("pulse:newspaper-update", args=[self.newspaper.pk]),
            {
                "title": "Updated Title",
                "content": "Updated content",
                "published_date": "2022-01-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.newspaper.refresh_from_db()
        self.assertEqual(self.newspaper.title, "Updated Title")


class NewspaperDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.newspaper = Newspaper.objects.create(
            title="To be deleted",
            content="Content",
            published_date="2020-01-01"
        )

    def setUp(self):
        get_user_model().objects.create_user(
            username="testuser",
            password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_delete_newspaper(self):
        response = self.client.post(
            reverse("pulse:newspaper-delete", args=[self.newspaper.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Newspaper.objects.filter(
            pk=self.newspaper.pk).exists()
                         )
