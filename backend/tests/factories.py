import factory
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    full_name = "Test User"
    role = User.Role.TRADER
    status = User.Status.ACTIVE


class AdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"admin{n}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "AdminPass123!")
    full_name = "Admin User"
    role = User.Role.ADMIN
    status = User.Status.ACTIVE
    is_staff = True
    is_superuser = True


def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}
