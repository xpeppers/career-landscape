import factory

class CircleFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'clusters.Circle'
        django_get_or_create = ('name',)

    name = 'circle'