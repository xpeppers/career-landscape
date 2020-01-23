import factory

from .topic import TopicFactory

class DimensionFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'clusters.Dimension'
        django_get_or_create = ('name','topic')

    name = factory.Sequence(lambda n: 'dimension%d' % n)
    topic = factory.SubFactory(TopicFactory)