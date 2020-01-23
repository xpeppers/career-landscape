from clusters.models import Circle, Topic, Dimension, Score
from django.contrib.auth.models import User

from .circle import CircleFactory
from .topic import TopicFactory
from .dimension import DimensionFactory
from .score import ScoreFactory
from .user import UserFactory


def create_sample_with_score_values(values):
    circle = CircleFactory.create(name='circle')
    person = UserFactory.build()
    person.save()
    topics = [TopicFactory.create(name=f'topic{n}', circle=circle) for n in range(len(values)) ]
    dimensions = [ DimensionFactory.create(topic=a_topic) for a_topic in topics ]
    scores = [ ScoreFactory.create(person=person, dimension=dimensions[i], value=values[i]) for i in range(len(values)) ]


def create_users(number):
    people = []
    for i in range(number):
        user = UserFactory.build(username=f'user{i}')
        user.save()
        people.append(user)
    return people