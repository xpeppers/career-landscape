from django.contrib.auth.models import User
import factory

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username','email','password')

    email = 'admin@admin.com'
    username = 'admin'
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')