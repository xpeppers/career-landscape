from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Circle, Topic

class TopicModelTest(TestCase):

    def test_unique_constraint_topic_circle(self):
        circle = Circle(name='testCircle')
        circle.save()

        topic = Topic(name='testTopic',circle=circle)
        topic.save()

        with self.assertRaises(IntegrityError):
            topic_double = Topic(name='testTopic',circle=circle)
            topic_double.save()
