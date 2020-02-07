from django.contrib.auth.models import User
import factory


class UserFactory(factory.DjangoModelFactory):
    class Meta:
<<<<<<< HEAD
        model = 'auth.User'
        django_get_or_create = ('username', 'email', 'password', 'first_name', 'last_name', 'is_staff')

    email = 'admin@admin.com'
    username = 'admin'
    first_name = 'admin_first_name'
    last_name = 'admin_last_name'
    is_staff = False
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')
=======
        model = "auth.User"
        django_get_or_create = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

    email = "admin@admin.com"
    username = "admin"
    first_name = "admin_first_name"
    last_name = "admin_last_name"
    password = factory.PostGenerationMethodCall("set_password", "adm1n")
>>>>>>> 7ac65ab34141a564ce09a0b8f5e5fbf22032a214
