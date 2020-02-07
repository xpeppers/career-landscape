from django.test import TestCase
from django.db.utils import IntegrityError

from clusters.tests.factories.factory_methods import *

from clusters.models import Circle, Topic, Dimension, Score
from clusters.tests.factories.circle import CircleFactory
from clusters.tests.factories.topic import TopicFactory


class TopicModelTest(TestCase):
    def test_circle_cant_have_same_topic_twice(self):
        circle = CircleFactory.create(name="testCircle")
        topic_name = "testTopic"

        topic = Topic(name=topic_name, circle=circle)
        topic.save()

        with self.assertRaises(IntegrityError):
            topic_double = Topic(name=topic_name, circle=circle)
            topic_double.save()

    def test_different_circles_can_have_same_topic(self):
        circle = CircleFactory.create(name="testCircle")
        circle_two = CircleFactory.create(name="testCircle_two")
        topic_name = "testTopic"

        topic = Topic(name=topic_name, circle=circle)
        topic.save()
        topic_double = Topic(name=topic_name, circle=circle_two)
        topic_double.save()

        self.assertEqual(topic_double.name, topic.name)


class DimensionModelTest(TestCase):
    def test_topic_cant_have_same_dimension_twice(self):
        circle = CircleFactory.create(name="testCircle")
        topic = TopicFactory.create(name="testTopic", circle=circle)
        dimension_name = "testDimension"

        dimension = Dimension(name=dimension_name, topic=topic)
        dimension.save()

        with self.assertRaises(IntegrityError):
            dimension_double = Dimension(name=dimension_name, topic=topic)
            dimension_double.save()

    def test_different_topics_can_have_same_dimension(self):
        circle = CircleFactory.create(name="testCircle")
        topic = TopicFactory.create(name="testTopic", circle=circle)
        topic_two = TopicFactory.create(name="testTopic_two", circle=circle)
        dimension_name = "testDimension"

        dimension = Dimension(name=dimension_name, topic=topic)
        dimension.save()
        dimension_double = Dimension(name=dimension_name, topic=topic_two)
        dimension_double.save()

        self.assertEqual(dimension.name, dimension_double.name)


class ScoreModelTest(TestCase):
    def test_different_score_have_different_date_field(self):
        create_sample_with_score_values([1, 2])

        scores = Score.objects.all()
        first_score = scores.first()
        second_score = scores.last()

        self.assertNotEqual(first_score.date, second_score.date)
