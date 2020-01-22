from django.test import TestCase, Client
from django.db.utils import IntegrityError
from django.contrib.auth.models import User


from clusters.tests.factories.factory_methods import *

from clusters.models import Circle, Topic, Dimension, Score
from clusters.views import IndexView
from  clusters.tests.factories.circle import CircleFactory
from  clusters.tests.factories.topic import TopicFactory
from  clusters.tests.factories.dimension import DimensionFactory


class IndexViewTest(TestCase):
    def test_index_shows_cirle_and_topics_names(self):
        client = Client()
        topic_name = "testTopic"
        circle_name = "testCircle"
        circle = CircleFactory.create(name=circle_name)
        topic = TopicFactory.create(name=topic_name, circle=circle)

        response = client.get("/")
        self.assertContains(response, circle_name)
        self.assertContains(response, topic_name)

    def test_index_with_no_circle_print_message(self):
        client = Client()

        response = client.get("/")
        self.assertContains(response, "No Circle available.")

    def test_index_with_no_topic_in_circle_print_message(self):
        client = Client()
        circle = CircleFactory.create()
        circle.save()

        response = client.get("/")
        self.assertContains(response, "No Topics available.")

    def test_index_shows_topics_numbers(self):
        client = Client()
        create_sample_with_score_values([1, 1, 0, 1])

        response = client.get("/")
        self.assertContains(response, "topic0 : 1")
        self.assertContains(response, "topic1 : 1")
        self.assertContains(response, "topic2 : 0")
        self.assertContains(response, "topic3 : 1")

    def test_filtered_view_shows_only_selected_range_of_values(self):
        client = Client()
        create_sample_with_score_values([1, 5, 4, 2])

        response = client.get("/", {'topic_value_gt' : 3})
        self.assertContains(response, "topic0 : 0")
        self.assertContains(response, "topic1 : 1")
        self.assertContains(response, "topic2 : 1")
        self.assertContains(response, "topic3 : 0")

    def test_filtered_view_shows_only_selected_dimensions_score(self):
        client = Client()
        circle = CircleFactory.create()
        topic = TopicFactory.create(circle=circle)
        dimension_one = DimensionFactory.create(name="dimension_one", topic=topic)
        dimension_two = DimensionFactory.create(name="dimension_two", topic=topic)
        people = create_users(2)

        score_first = Score(person=people[0], dimension=dimension_one, value=5)
        score_first.save()
        score_second = Score(person=people[1], dimension=dimension_two, value=5)
        score_second.save()

        response = client.get("/", {'topic_dimension_eq' : 'dimension_one'})
        self.assertContains(response, "topic : 1")

    def test_index_add_expected_context(self):
        create_sample_with_score_values([1, 1, 0, 1])
        index = IndexView()

        context = index.add_first_cirle_context({})

        self.assertEqual(context["circle_name"], "circle")
        topics_details = {"topic0": 1, "topic1": 1, "topic2": 0, "topic3": 1}
        self.assertEqual(context["topics_details"], topics_details)

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

