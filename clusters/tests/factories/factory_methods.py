from clusters.models import Circle, Topic, Dimension, Score
from django.test import Client
from django.contrib.auth.models import User
import pandas

from .circle import CircleFactory
from .topic import TopicFactory
from .dimension import DimensionFactory
from .score import ScoreFactory
from .user import UserFactory


def create_sample_with_score_values(values):
    circle = CircleFactory.create(name="circle")
    person = UserFactory.build()
    person.save()
    topics = [
        TopicFactory.create(name=f"topic{n}", circle=circle) for n in range(len(values))
    ]
    dimensions = [DimensionFactory.create(topic=a_topic) for a_topic in topics]
    scores = [
        ScoreFactory.create(person=person, dimension=dimensions[i], value=values[i])
        for i in range(len(values))
    ]


def create_users(number):
    people = []
    for i in range(number):
        user = UserFactory.build(username=f"user{i}")
        user.save()
        people.append(user)
    return people


def create_example_excel_file_context():
    user = UserFactory.build(
        username="username",
        first_name="user_name",
        last_name="user_surname",
        password="us_test_ps_w",
    )
    user.save()
    circle = CircleFactory.create(name="Circle")
    topics = [TopicFactory.create(name=f"topic{i}", circle=circle) for i in range(1, 3)]
    dimension_topic_1 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics[0])
        for i in range(1, 5)
    ]
    dimension_topic_2 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics[1])
        for i in range(1, 5)
    ]


def create_example_excel_file_topics_numbers():
    user = UserFactory.build(
        username="username",
        first_name="user_name",
        last_name="user_surname",
        password="us_test_ps_w",
    )
    user.save()
    circle1 = CircleFactory.create(name="Circle1")
    circle2 = CircleFactory.create(name="Circle2")
    topics1 = [
        TopicFactory.create(name=f"topic{i}", circle=circle1) for i in range(1, 3)
    ]
    topics2 = [
        TopicFactory.create(name=f"topic{i}", circle=circle2) for i in range(1, 4)
    ]
    dimension1_topic_1 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics1[0])
        for i in range(1, 5)
    ]
    dimension1_topic_2 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics1[1])
        for i in range(1, 5)
    ]
    dimension2_topic_1 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics2[0])
        for i in range(1, 5)
    ]
    dimension2_topic_2 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics2[1])
        for i in range(1, 5)
    ]
    dimension2_topic_3 = [
        DimensionFactory.create(name=f"dimension{i}", topic=topics2[2])
        for i in range(1, 5)
    ]


def get_logged_superuser_client():
    username = "myuser"
    password = "myusmypass"
    user = UserFactory.build(
        username=username, password=password, is_superuser=True, is_staff=True
    )
    user.save()
    client = Client()
    client.login(username=username, password=password)
    return client
