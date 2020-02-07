import factory

from .dimension import DimensionFactory
from .user import UserFactory
from django.contrib.auth.models import User


class ScoreFactory(factory.DjangoModelFactory):
    class Meta:
<<<<<<< HEAD
        model = 'clusters.Score'
        django_get_or_create = ('dimension','person','value','kind')
=======
        model = "clusters.Score"
        django_get_or_create = ("dimension", "person", "value")
>>>>>>> 7ac65ab34141a564ce09a0b8f5e5fbf22032a214

    dimension = factory.SubFactory(DimensionFactory)
    person = factory.SubFactory(UserFactory)
    value = 1
<<<<<<< HEAD
    kind = 0
=======
>>>>>>> 7ac65ab34141a564ce09a0b8f5e5fbf22032a214
