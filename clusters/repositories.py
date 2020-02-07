from .models import Circle, Score, Topic, Dimension
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

class UserRepository():

    def get_user_by_first_name_and_last_name(self, first_name, last_name):
        try:
            return User.objects.get(first_name=first_name, last_name=last_name)
        except ObjectDoesNotExist as _:
            return None
        except MultipleObjectsReturned as _:
            return None

class CircleRepository():

    def get_all_circles(self):
        return Circle.objects.all()

    def get_circle_by_name(self, name):
        try:
            return Circle.objects.get(name=name)
        except Circle.DoesNotExist as _ :
            return None

class ScoreRepository():

    def save_score(self, dimension, person, value, date, kind):
        Score(
            dimension=dimension,
            person=person,
            value=value,
            date=date,
            kind=kind).save()


class TopicRepository():

    def get_topic_by_name_and_circle(self, name, circle):
        try:
            return Topic.objects.get(circle=circle, name=name)
        except Topic.DoesNotExist as _ :
            return None

class DimensionRepository():

    def get_dimension_by_name_and_topic(self, name, topic):
        try:
            return Dimension.objects.get(topic=topic, name=name)
        except Dimension.DoesNotExist as _ :
            return None