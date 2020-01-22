import factory

from .topic import TopicFactory

class DimensionFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'clusters.Dimension'
        django_get_or_create = ('name','topic')

    name = 'dimension'
    topic = factory.SubFactory(TopicFactory)