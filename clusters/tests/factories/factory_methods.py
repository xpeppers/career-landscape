from clusters.models import Circle, Topic, Dimension, Score
from django.contrib.auth.models import User
import pandas

from .circle import CircleFactory
from .topic import TopicFactory
from .dimension import DimensionFactory
from .score import ScoreFactory
from .user import UserFactory


def create_sample_with_score_values(values):
    circle = CircleFactory.create(name='circle')
    person = UserFactory.build()
    person.save()
    topics = [ TopicFactory.create(name=f'topic{n}', circle=circle) for n in range(len(values)) ]
    dimensions = [ DimensionFactory.create(topic=a_topic) for a_topic in topics ]
    scores = [ ScoreFactory.create(person=person, dimension=dimensions[i], value=values[i]) for i in range(len(values)) ]


def create_users(number):
    people = []
    for i in range(number):
        user = UserFactory.build(username=f'user{i}')
        user.save()
        people.append(user)
    return people

def create_example_excel_file_context():
    user = UserFactory.build(username='username', first_name='user_name', last_name='user_surname', password='us_test_ps_w')
    user.save()
    circle = CircleFactory.create(name='Circle')
    topics = [ TopicFactory.create(name=f"topic{i}", circle=circle) for i in range(1,3) ]
    dimension_topic_1 = [ DimensionFactory.create(name=f"dimension{i}", topic=topics[0]) for i in range(1,5) ]
    dimension_topic_2 = [ DimensionFactory.create(name=f"dimension{i}", topic=topics[1]) for i in range(1,5) ]