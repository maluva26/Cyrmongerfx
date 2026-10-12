import pytest


@pytest.mark.django_db
def test_smoke(api_client):
    r = api_client.get("/api/v1/health")
    assert r.status_code == 200
