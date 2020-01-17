from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Circle, Topic, Dimension


class TopicModelTest(TestCase):

    def test_unique_constraint_topic_circle(self):
        circle = Circle(name='testCircle')
        circle.save()

        topic = Topic(name='testTopic',circle=circle)
        topic.save()

        with self.assertRaises(IntegrityError):
            topic_double = Topic(name='testTopic',circle=circle)
            topic_double.save()


class DimensionModelTest(TestCase):

    def test_unique_constraint_dimension_topic(self):
        circle = Circle(name='testCircle')
        circle.save()
        topic = Topic(name='testTopic',circle=circle)
        topic.save()

        dimension = Dimension(name='testDimension',topic=topic)
        dimension.save()

        with self.assertRaises(IntegrityError):
            dimension = Dimension(name='testDimension',topic=topic)
            dimension.save()
