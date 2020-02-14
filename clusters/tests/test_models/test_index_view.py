from django.test import RequestFactory, TestCase, Client
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
import pandas

from clusters.tests.factories.factory_methods import *

from clusters.models import Circle, Topic, Dimension, Score
from clusters.views import IndexView
from clusters.tests.factories.circle import CircleFactory
from clusters.tests.factories.topic import TopicFactory
from clusters.tests.factories.dimension import DimensionFactory


class IndexViewTest(TestCase):
    def test_index_shows_cirle_and_topics_names(self):
        client = get_logged_superuser_client()
        topic_name = "testTopic"
        circle_name = "testCircle"
        circle = CircleFactory.create(name=circle_name)
        topic = TopicFactory.create(name=topic_name, circle=circle)

        response = client.get("/")
        self.assertContains(response, circle_name)
        self.assertContains(response, topic_name)

    def test_index_with_no_circle_print_message(self):
        client = get_logged_superuser_client()

        response = client.get("/")
        self.assertContains(response, "No Circle available.")

    def test_index_with_no_topic_in_circle_print_message(self):
        client = get_logged_superuser_client()
        circle = CircleFactory.create()
        circle.save()

        response = client.get("/")
        self.assertContains(response, "No Topics available.")

    def test_index_shows_topics_numbers(self):
        client = get_logged_superuser_client()
        create_sample_with_score_values([1, 1, 0, 1])

        response = client.get("/")

        self.assertContains(
            response, 'topic0 : <span class="badge dark-grey-bg text-white">1</span>'
        )
        self.assertContains(
            response, 'topic1 : <span class="badge dark-grey-bg text-white">1</span>'
        )
        self.assertContains(
            response, 'topic2 : <span class="badge dark-grey-bg text-white">0</span>'
        )
        self.assertContains(
            response, 'topic3 : <span class="badge dark-grey-bg text-white">1</span>'
        )

    def test_filtered_view_shows_only_selected_range_of_values(self):
        client = get_logged_superuser_client()
        create_sample_with_score_values([1, 5, 4, 2])
        circle_id = Topic.objects.filter(name="topic0").first().circle.id

        response = client.get("/", {f"topic_value_gt_{circle_id}": 3})
        self.assertContains(
            response, 'topic0 : <span class="badge dark-grey-bg text-white">0</span>'
        )
        self.assertContains(
            response, 'topic1 : <span class="badge dark-grey-bg text-white">1</span>'
        )
        self.assertContains(
            response, 'topic2 : <span class="badge dark-grey-bg text-white">1</span>'
        )
        self.assertContains(
            response, 'topic3 : <span class="badge dark-grey-bg text-white">0</span>'
        )

    def test_filtered_view_shows_only_selected_dimensions_score(self):
        client = get_logged_superuser_client()
        circle = CircleFactory.create()
        topic = TopicFactory.create(name="topic", circle=circle)
        dimension_one = DimensionFactory.create(name="dimension_one", topic=topic)
        dimension_two = DimensionFactory.create(name="dimension_two", topic=topic)
        people = create_users(2)

        score_first = Score(person=people[0], dimension=dimension_one, value=5)
        score_first.save()
        score_second = Score(person=people[1], dimension=dimension_two, value=5)
        score_second.save()

        response = client.get(
            "/", {f"topic_dimension_eq_{circle.id}": dimension_one.id}
        )
        self.assertContains(
            response, 'topic : <span class="badge dark-grey-bg text-white">1</span>'
        )

    def test_index_add_expected_context(self):
        create_sample_with_score_values([1, 1, 0, 1])
        topics_names = ["topic0", "topic1", "topic2", "topic3"]
        self.factory = RequestFactory()
        request = self.factory.get("/")
        index = IndexView()
        index.setup(request)

        context = index.add_circles_context({})
        self.assertNotEqual(context.get("circles"), None)
        circle = context["circles"]
        self.assertNotEqual(circle.get("circle"), None)

        topics_details = circle["circle"]["topics_details"]
        for topic_name in topics_names:
            self.assertNotEqual(topics_details.get(topic_name), None)

    def test_count_people_in_topic_return_expected_value(self):
        circle = CircleFactory.create()
        topic = TopicFactory(circle=circle)
        dimension = DimensionFactory(topic=topic)
        dimension.save()
        people = create_users(2)

        score_first = Score(person=people[0], dimension=dimension, value=0)
        score_first.save()
        score_second = Score(person=people[1], dimension=dimension, value=1)
        score_second.save()

        index = IndexView()
        value = index.count_people_in_topic(topic)

        self.assertEqual(value, 1)

    def test_index_view_shows_all_circle_names(self):
        client = get_logged_superuser_client()
        circles = [CircleFactory.create() for _ in range(4)]
        circles_names = [circle.name for circle in circles]

        response = client.get("/")

        for name in circles_names:
            self.assertContains(response, name)

    def test_index_view_shows_all_topics_of_different_circles(self):
        client = get_logged_superuser_client()
        first_circle = CircleFactory.create()
        second_circle = CircleFactory.create()
        first_circle_topics = [
            TopicFactory.create(circle=first_circle) for _ in range(3)
        ]
        second_circle_topics = [
            TopicFactory.create(circle=second_circle) for _ in range(3)
        ]

        response = client.get("/")

        topics_names = [topic.name for topic in first_circle_topics] + [
            topic.name for topic in second_circle_topics
        ]
        for topic_name in topics_names:
            self.assertContains(response, topic_name)

    def test_alter_circle_value_filter_not_alter_others_circle_value_filter(self):
        client = get_logged_superuser_client()
        person = create_users(1)[0]
        first_circle = CircleFactory.create()
        second_circle = CircleFactory.create()
        first_circle_topic = TopicFactory.create(circle=first_circle)
        second_circle_topic = TopicFactory.create(circle=second_circle)
        first_circle_dimension = DimensionFactory.create(topic=first_circle_topic)
        second_circle_dimension = DimensionFactory.create(topic=second_circle_topic)
        first_circle_score = ScoreFactory.create(
            dimension=first_circle_dimension, value=3, person=person
        )
        second_circle_score = ScoreFactory.create(
            dimension=second_circle_dimension, value=3, person=person
        )

        response = client.get("/", {f"topic_value_gt_{first_circle.id}": 4})

        self.assertContains(
            response,
            f'{first_circle_topic.name} : <span class="badge dark-grey-bg text-white">0</span>',
        )
        self.assertContains(
            response,
            f'{second_circle_topic.name} : <span class="badge dark-grey-bg text-white">1</span>',
        )

    def test_alter_circle_dimension_filter_not_alter_others_circle_dimension_filter(
        self,
    ):
        client = get_logged_superuser_client()
        person = create_users(1)[0]
        first_circle = CircleFactory.create()
        second_circle = CircleFactory.create()
        first_circle_topic = TopicFactory.create(circle=first_circle)
        second_circle_topic = TopicFactory.create(circle=second_circle)
        first_circle_dimension_populated = DimensionFactory.create(
            name="dimension_1", topic=first_circle_topic
        )
        first_circle_dimension_empty = DimensionFactory.create(
            name="dimension_2", topic=first_circle_topic
        )
        second_circle_dimension = DimensionFactory.create(
            name="dimension_1", topic=second_circle_topic
        )
        first_circle_score = ScoreFactory.create(
            dimension=first_circle_dimension_populated, person=person
        )
        second_circle_score = ScoreFactory.create(
            dimension=second_circle_dimension, person=person
        )

        response = client.get(
            "/",
            {
                f"topic_dimension_eq_{first_circle.id}": f"{first_circle_dimension_empty.id}"
            },
        )

        self.assertContains(
            response,
            f'{first_circle_topic.name} : <span class="badge dark-grey-bg text-white">0</span>',
        )
        self.assertContains(
            response,
            f'{second_circle_topic.name} : <span class="badge dark-grey-bg text-white">1</span>',
        )

    def test_not_logged_person_accessing_index_will_be_redirect_to_login_page(self):
        client = Client()

        response = client.get("/", follow=True)

        self.assertContains(response, "Login")

    def test_normal_logged_user_can_access_index_view(self):
        user_username = "firstuser"
        user_psw = "mypasspass"
        user = UserFactory.build(username=user_username, password=user_psw)
        user.save()
        client = Client()
        client.login(username=user_username, password=user_psw)

        response = client.get("/")

        self.assertContains(response, "No Circle available")
