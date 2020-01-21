from django.test import TestCase, Client
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from .models import Circle, Topic, Dimension, Score
from .views import IndexView

class TopicModelTest(TestCase):

    def test_circle_cant_have_same_topic_twice(self):
        circle = Circle(name='testCircle')
        circle.save()
        topic_name = 'testTopic'

        topic = Topic(name=topic_name, circle=circle)
        topic.save()

        with self.assertRaises(IntegrityError):
            topic_double = Topic(name=topic_name, circle=circle)
            topic_double.save()

    def test_different_circles_can_have_same_topic(self):
        circle = Circle(name='testCircle')
        circle.save()
        circle_two = Circle(name='testCircle_two')
        circle_two.save()
        topic_name = 'testTopic'

        topic = Topic(name=topic_name, circle=circle)
        topic.save()
        topic_double = Topic(name=topic_name, circle=circle_two)
        topic_double.save()

        self.assertEqual(topic_double.name, topic.name)

class DimensionModelTest(TestCase):

    def test_topic_cant_have_same_dimension_twice(self):
        circle = Circle(name='testCircle')
        circle.save()
        topic = Topic(name='testTopic', circle=circle)
        topic.save()
        dimension_name = 'testDimension'

        dimension = Dimension(name=dimension_name, topic=topic)
        dimension.save()

        with self.assertRaises(IntegrityError):
            dimension_double = Dimension(name=dimension_name, topic=topic)
            dimension_double.save()

    def test_different_topics_can_have_same_dimension(self):
        circle = Circle(name='testCircle')
        circle.save()
        topic = Topic(name='testTopic', circle=circle)
        topic.save()
        topic_two = Topic(name='testTopic_two', circle=circle)
        topic_two.save()
        dimension_name = 'testDimension'

        dimension = Dimension(name=dimension_name, topic=topic)
        dimension.save()
        dimension_double = Dimension(name=dimension_name, topic=topic_two)
        dimension_double.save()

        self.assertEqual(dimension.name, dimension_double.name)


class IndexViewTest(TestCase):

    def test_index_shows_cirle_and_topics_names(self):
        client = Client()
        topic_name = 'testTopic'
        circle_name = 'testCircle'
        circle = Circle(name=circle_name)
        circle.save()
        topic = Topic(name=topic_name, circle=circle)
        topic.save()

        response = client.get('/clusters/')
        self.assertContains(response,circle_name)
        self.assertContains(response,topic_name)

    def test_index_with_no_circle_print_message(self):
        client = Client()

        response = client.get('/clusters/')
        self.assertContains(response,'No Circle available.')

    def test_index_with_no_topic_in_circle_print_message(self):
        client = Client()
        circle = Circle(name='testCircle')
        circle.save()

        response = client.get('/clusters/')
        self.assertContains(response,'No Topics available.')

    def test_index_shows_topics_numbers(self):
        client = Client()
        self.set_sample_with_score_values([1,1,0,1])

        response = client.get('/clusters/')
        self.assertContains(response,'topic0 : 1')
        self.assertContains(response,'topic1 : 1')
        self.assertContains(response,'topic2 : 0')
        self.assertContains(response,'topic3 : 1')

    def test_index_add_expected_context(self):
        self.set_sample_with_score_values([1,1,0,1])
        index = IndexView()

        context = index.add_first_cirle_context({})

        self.assertEqual(context['circle_name'], 'circle')
        topics_details = {'topic0': 1, 'topic1': 1, 'topic2': 0, 'topic3': 1}
        self.assertEqual(context['topics_details'], topics_details)

    def test_count_people_in_topic_return_expected_value(self):
        circle = Circle(name='circle')
        circle.save()
        topic_name = 'topic'
        topic = Topic(name=topic_name,circle=circle)
        topic.save()
        dimension = Dimension(name="dimension", topic=topic)
        dimension.save()
        person = User.objects.create_user(username='user_username', email='user_mail', password='user_password')
        person_two = User.objects.create_user(username='user_username_two', email='user_mail_two', password='user_password_two')

        score_first = Score(person=person, dimension=dimension, value=0)
        score_first.save()
        score_second = Score(person=person_two, dimension=dimension, value=1)
        score_second.save()

        index = IndexView()
        value = index.count_people_in_topic(topic)

        self.assertEqual(value, 1)

    def set_sample_with_score_values(self, values):
        person = User.objects.create_user(username='user_username', email='user_mail', password='user_password')
        circle = Circle(name='circle')
        circle.save()
        for i in range(0,len(values)):
            topic_name = 'topic'+str(i)
            self.set_score(circle, topic_name, 'dimension', person, values[i])

    def set_score( self, circle, topic_name, dimension_name, person, value ):
        topic = Topic(name=topic_name, circle=circle)
        topic.save()
        dimension = Dimension(name=dimension_name, topic=topic)
        dimension.save()
        score = Score(person=person, dimension=dimension, value=value)
        score.save()
