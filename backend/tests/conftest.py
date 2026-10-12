import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_cache():
    """Keep the shared locmem cache from leaking state between tests."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def disable_throttling(settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "anon": "1000/day",
            "user": "10000/day",
            "auth": "1000/min",
            "analyze": "1000/hour",
            "assistant": "1000/day",
            "feedback": "1000/day",
            "internal": "1000/day",
        },
    }


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="TestPass123!", full_name="Test User")


@pytest.fixture
def admin(db):
    return User.objects.create_superuser(email="admin@test.com", password="AdminPass123!", full_name="Admin")


@pytest.fixture
def trader_client(api_client, user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@test.com", password="OtherPass123!", full_name="Other")


@pytest.fixture
def other_client(api_client, other_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(other_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture(autouse=True)
def mock_storage(settings):
    from unittest.mock import patch
    from apps.charts.storage import LocalDevChartStorage

    with patch("apps.charts.views.get_chart_storage", return_value=LocalDevChartStorage()):
        yield
