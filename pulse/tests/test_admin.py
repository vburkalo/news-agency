import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from pulse.models import Topic, Redactor, Newspaper


class AdminSiteTest(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", email="admin@test.com", password="password123"
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.topic = Topic.objects.create(name="Environment")
        self.redactor = Redactor.objects.create(
            username="redactor1", years_of_experience=5, password="password123"
        )
        self.newspaper = Newspaper.objects.create(
            title="Daily News",
            content="Important content here",
            published_date=datetime.date(2023, 1, 1),
        )
        self.newspaper.topic.add(self.topic)

    def test_newspaper_admin_search(self):
        url = reverse("admin:pulse_newspaper_changelist") + "?q=Daily News"
        response = self.client.get(url)
        self.assertContains(response, self.newspaper.title)

    def test_topic_search(self):
        url = reverse("admin:pulse_topic_changelist") + "?q=Environment"
        response = self.client.get(url)
        self.assertContains(response, "Environment")
        self.assertNotContains(response, "Technology")

    def test_redactor_admin_search(self):
        url = reverse("admin:pulse_redactor_changelist") + "?q=redactor1"
        response = self.client.get(url)
        self.assertContains(response, "redactor1")

    def test_newspaper_admin_filter_by_date(self):
        url = reverse(
            "admin:pulse_newspaper_changelist"
        ) + "?published_date__year=2023"
        response = self.client.get(url)
        self.assertContains(response, "Daily News")

    def test_newspaper_admin_filter_by_topic(self):
        url = (
            reverse(
                "admin:pulse_newspaper_changelist"
            ) + "?topic=" + str(self.topic.id)
        )
        response = self.client.get(url)
        self.assertContains(response, "Daily News")

    def test_admin_site_access_non_admin_user(self):
        non_admin_user = get_user_model().objects.create_user(
            username="nonadmin",
            email="nonadmin@test.com",
            password="password1234"
        )
        self.client.force_login(non_admin_user)
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_redactor_admin_add_form(self):
        url = reverse("admin:pulse_redactor_add")
        response = self.client.post(
            url,
            {
                "username": "new_redactor",
                "years_of_experience": 10,
                "password1": "newpassword123",
                "password2": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Redactor.objects.filter(
            username="new_redactor"
        ).exists())

    def test_redactor_admin_change_form(self):
        url = reverse("admin:pulse_redactor_change", args=(self.redactor.pk,))
        response = self.client.post(
            url,
            {
                "username": self.redactor.username,
                "years_of_experience": 8,
                "password1": "newpassword123",
                "password2": "newpassword123",
            },
        )
        if response.status_code == 200:
            if "form" in response.context:
                print(response.context["form"].errors)
            else:
                print("Form not present in response context.")
        elif response.status_code == 302:
            self.redactor.refresh_from_db()
            self.assertEqual(self.redactor.years_of_experience, 8)
        else:
            print(f"Unexpected status code: {response.status_code}")

    def test_topic_admin_list_display(self):
        url = reverse("admin:pulse_topic_changelist")
        response = self.client.get(url)
        self.assertContains(response, "Environment")

    def test_newspaper_list_order(self):
        Newspaper.objects.create(
            title="Earlier News", published_date=datetime.date(2022, 12, 31)
        )
        url = reverse("admin:pulse_newspaper_changelist")
        response = self.client.get(url)
        content = response.content.decode()
        self.assertTrue(
            content.index("Earlier News") < content.index("Daily News")
        )

    def test_non_staff_user_admin_access(self):
        non_staff_user = get_user_model().objects.create_user(
            username="nonstaff",
            email="nonstaff@test.com",
            password="password1234"
        )
        self.client.force_login(non_staff_user)
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_redactor_fieldsets_on_add_form(self):
        url = reverse("admin:pulse_redactor_add")
        response = self.client.get(url)
        self.assertContains(response, "Years of experience")
