from django.contrib.auth.models import User
import factory

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username', 'email', 'password', 'first_name', 'last_name', 'is_staff')

    email = 'admin@admin.com'
    username = 'admin'
    first_name = 'admin_first_name'
    last_name = 'admin_last_name'
    is_staff = False
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')