from django.test import TestCase, Client

from clusters.tests.factories.user import UserFactory
from clusters.tests.factories.factory_methods import *


class UserViewTest(TestCase):
    def test_user_view_display_correct_dimension_value(self):
        client = get_logged_staff_client()
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
        client = get_logged_staff_client()
        first_name = "user_f_n"
        last_name = "user_l_n"
        user = UserFactory.build(first_name=first_name, last_name=last_name)
        user.save()

        response = client.get(f"/users/{user.id}", follow=True)

        self.assertContains(response, first_name)
        self.assertContains(response, last_name)

    def test_user_view_display_circles_names(self):
        client = get_logged_staff_client()
        circles = [CircleFactory.create(name=f"circle{i}") for i in range(3)]
        user = UserFactory.build()
        user.save()

        response = client.get(f"/users/{user.id}", follow=True)

        for i in range(3):
            self.assertContains(response, f"circle{i}")

    def test_user_view_display_topics_names_of_selected_circle(self):
        client = get_logged_staff_client()
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
        client = get_logged_staff_client()
        circle_name = "circle"
        user_first_name = "user_f_n"
        user_last_name = "user_l_n"
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
        self.assertContains(response, f"by { user_first_name } { user_last_name }")

    def test_user_view_momentum_filter_is_in_template_context_if_applied(self):
        client = get_logged_staff_client()
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
            f"/users/{user.id}",
            {
                "selected_user_circle": circle.id,
                "momentum": "on",
                "selected_topic": topic.name,
            },
            follow=True,
        )

        self.assertEqual(response.context["apply_momentum_to_radar"], True)
        self.assertEqual(response.context["selected_topic"], topic.name)

    def test_user_view_next_step_filter_is_in_template_context_if_applied(self):
        client = get_logged_staff_client()
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
            f"/users/{user.id}",
            {
                "selected_user_circle": circle.id,
                "next-step": "on",
                "selected_topic": topic.name,
            },
            follow=True,
        )

        self.assertEqual(response.context["apply_next_step_to_radar"], True)
        self.assertEqual(response.context["selected_topic"], topic.name)
