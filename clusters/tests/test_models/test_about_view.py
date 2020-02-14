from django.test import TestCase
from django.test import Client


class AboutViewTest(TestCase):
    def test_not_logged_user_can_access_about_view(self):
        client = Client()

        response = client.get("/about/")

        self.assertContains(response, "Welcome in Career Landscape")
