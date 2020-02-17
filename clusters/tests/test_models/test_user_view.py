from django.test import TestCase, Client

from clusters.tests.factories.user import UserFactory
from clusters.tests.factories.factory_methods import *


class UserViewTest(TestCase):
    def test_user_view_display_correct_dimension_value(self):
        client = get_logged_superuser_client()
        user = UserFactory.build(first_name="user_f_n", last_name="user_l_n")
        user.save()
        circle = CircleFactory.create()
        topic = TopicFactory.create(circle=circle)
        dimension = DimensionFactory.create(topic=topic)
        scores = [
            ScoreFactory.create(person=user, dimension=dimension, kind=i)
            for i in range(0, 3)
        ]

        response = client.get(
            f"/users/{user.id}", {"selected_user_circle": circle.id}, follow=True
        )

        self.assertContains(
            response, f'<span class="badge badge-secondary red-bg">{scores[0].value}'
        )
        self.assertContains(
            response, f'<span class="badge badge-secondary yellow-bg">{scores[1].value}'
        )
        self.assertContains(
            response, f'<span class="badge badge-secondary green-bg">{scores[2].value}'
        )

    def test_user_view_display_user_first_and_last_name(self):
        client = get_logged_superuser_client()
        first_name = "userFirstName"
        last_name = "userLastName"
        user = UserFactory.build(first_name=first_name, last_name=last_name)
        user.save()

        response = client.get(f"/users/{user.id}", follow=True)

        self.assertContains(response, first_name.capitalize())
        self.assertContains(response, last_name.capitalize())

    def test_user_view_display_circles_names(self):
        client = get_logged_superuser_client()
        circles = [CircleFactory.create(name=f"circle{i}") for i in range(3)]
        user = UserFactory.build()
        user.save()

        response = client.get(f"/users/{user.id}", follow=True)

        for i in range(3):
            self.assertContains(response, f"circle{i}")

    def test_user_view_display_topics_names_of_selected_circle(self):
        client = get_logged_superuser_client()
        circle = CircleFactory.create()
        topics = [
            TopicFactory.create(name=f"topic{i}", circle=circle) for i in range(3)
        ]
        user = UserFactory.build()
        user.save()

        response = client.get(
            f"/users/{user.id}", {"selected_user_circle": circle.id}, follow=True
        )

        for i in range(3):
            self.assertContains(response, f"topic{i}")

    def test_user_view_display_error_message_if_user_access_circle_not_filled(self):
        client = get_logged_superuser_client()
        circle_name = "circle"
        user_first_name = "userfn"
        user_last_name = "userln"
        circle = CircleFactory.create(name=circle_name)
        topic = TopicFactory.create(circle=circle)
        dimension = DimensionFactory.create(topic=topic)
        user = UserFactory.build(first_name=user_first_name, last_name=user_last_name)
        user.save()

        response = client.get(
            f"/users/{user.id}", {"selected_user_circle": circle.id}, follow=True
        )

        self.assertContains(response, " - information not available - ")
        self.assertContains(response, f"The {circle_name} Circle")
        self.assertContains(
            response,
            f"by { user_first_name.capitalize() } { user_last_name.capitalize() }",
        )

    def test_normal_user_cannot_access_other_user_personal_page(self):
        user_1_username = "firstuser"
        user_1_psw = "mypasspass"
        user_1 = UserFactory.build(username=user_1_username, password=user_1_psw)
        user_1.save()
        user_2 = UserFactory.build()
        user_2.save()
        client = Client()
        client.login(username=user_1_username, password=user_1_psw)

        response = client.get(f"/users/{user_2.id}")

        self.assertContains(response, "We are sorry, you cannot access this page.")

    def test_a_user_can_access_his_personal_page(self):
        user_username = "firstuser"
        user_psw = "mypasspass"
        user_first_name = "userfn"
        user_last_name = "userln"
        user = UserFactory.build(
            username=user_username,
            password=user_psw,
            first_name=user_first_name,
            last_name=user_last_name,
        )
        user.save()
        client = Client()
        client.login(username=user_username, password=user_psw)

        response = client.get(f"/users/{user.id}")

        self.assertContains(
            response, f"{user_first_name.capitalize()} {user_last_name.capitalize()}"
        )

    def test_a_staff_user_can_access_all_users_pages(self):
        user_username = "firstuser"
        user_psw = "mypasspass"
        user = UserFactory.build(
            username=user_username, password=user_psw, is_staff=True,
        )
        user.save()
        first_name = "user2fn"
        last_name = "user2ln"
        user_2 = UserFactory.build(first_name=first_name, last_name=last_name)
        user_2.save()
        client = Client()
        client.login(username=user_username, password=user_psw)

        response = client.get(f"/users/{user_2.id}")

        self.assertContains(
            response, f"{first_name.capitalize()} {last_name.capitalize()}"
        )
