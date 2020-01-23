import factory

from .circle import CircleFactory

class TopicFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'clusters.Topic'
        django_get_or_create = ('name','circle')

    name = factory.Sequence(lambda n: 'topic%d' % n)
    circle = factory.SubFactory(CircleFactory)