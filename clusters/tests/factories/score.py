import factory

from .dimension import DimensionFactory
from .user import UserFactory
from django.contrib.auth.models import User

class ScoreFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'clusters.Score'
        django_get_or_create = ('dimension','person','value')

    dimension = factory.SubFactory(DimensionFactory)
    person = factory.SubFactory(UserFactory)
    value = 1