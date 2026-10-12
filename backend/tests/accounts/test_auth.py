import pytest
from rest_framework import status

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class TestAuth:
    def test_register_success(self, api_client):
        r = api_client.post("/api/v1/auth/register", {"email": "newuser@test.com", "password": "NewPass123!", "accepted_terms": True, "terms_version": "draft-2026-10"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@test.com").exists()

    def test_login_success(self, api_client, user):
        r = api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "TestPass123!"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.json()

    def test_login_invalid_email(self, api_client):
        r = api_client.post("/api/v1/auth/login", {"email": "nope@test.com", "password": "x"}, format="json")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED
        assert r.json()["error"]["message"] == "Invalid email or password"

    def test_login_lockout(self, api_client, user):
        for _ in range(5):
            api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "wrong"}, format="json")
        r = api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "wrong"}, format="json")
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_password_argon2(self, user):
        assert user.password.startswith("argon2$")

    def test_register_duplicate_email_rejected(self, api_client, user):
        r = api_client.post("/api/v1/auth/register", {"email": "user@test.com", "password": "StrongPass123!", "accepted_terms": True}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_requires_terms_acceptance(self, api_client):
        r = api_client.post("/api/v1/auth/register", {"email": "x@test.com", "password": "StrongPass123!", "accepted_terms": False}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_rejects_weak_password(self, api_client):
        r = api_client.post("/api/v1/auth/register", {"email": "x@test.com", "password": "short", "accepted_terms": True}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_sets_hardened_refresh_cookie(self, api_client, user, settings):
        """SEC-08: the refresh cookie must be HttpOnly, Secure and SameSite=Strict."""
        settings.REFRESH_COOKIE_SECURE = True
        r = api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "TestPass123!"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        cookie = r.cookies[settings.REFRESH_COOKIE_NAME]
        assert cookie["httponly"] is True
        assert cookie["secure"] is True
        assert cookie["samesite"] == "Strict"
        assert cookie["path"] == settings.REFRESH_COOKIE_PATH

    def test_logout_clears_refresh_cookie(self, trader_client, settings):
        r = trader_client.post("/api/v1/auth/logout", format="json")
        assert r.status_code == status.HTTP_204_NO_CONTENT
        assert r.cookies[settings.REFRESH_COOKIE_NAME]["max-age"] == 0

    def test_refresh_without_cookie_is_401(self, api_client):
        r = api_client.post("/api/v1/auth/refresh", format="json")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED
        assert r.json()["error"]["code"] == "REFRESH_REQUIRED"

    def test_refresh_with_cookie_returns_new_access_token(self, api_client, user):
        login = api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "TestPass123!"}, format="json")
        assert login.status_code == status.HTTP_200_OK
        r = api_client.post("/api/v1/auth/refresh", format="json")
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.json()

    def test_me_requires_auth(self, api_client):
        assert api_client.get("/api/v1/me").status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_patch_updates_full_name(self, trader_client):
        r = trader_client.patch("/api/v1/me", {"full_name": "New Name"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["full_name"] == "New Name"

    def test_password_change(self, trader_client, user):
        r = trader_client.post("/api/v1/auth/password/change", {"current_password": "TestPass123!", "new_password": "BrandNewPass456!"}, format="json")
        assert r.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password("BrandNewPass456!")

    def test_password_change_rejects_wrong_current(self, trader_client, user):
        r = trader_client.post("/api/v1/auth/password/change", {"current_password": "nope", "new_password": "BrandNewPass456!"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_CURRENT_PASSWORD"
        user.refresh_from_db()
        assert user.check_password("TestPass123!")

    def test_account_delete_requires_explicit_confirmation(self, trader_client, user):
        r = trader_client.delete("/api/v1/me", {"confirmation": "nope"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(pk=user.pk).exists()

    def test_account_delete(self, trader_client, user):
        r = trader_client.delete("/api/v1/me", {"confirmation": "DELETE"}, format="json")
        assert r.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user.pk).exists()

    def test_password_reset_request_does_not_leak_account_existence(self, api_client, user):
        known = api_client.post("/api/v1/auth/password/reset-request", {"email": "user@test.com"}, format="json")
        unknown = api_client.post("/api/v1/auth/password/reset-request", {"email": "ghost@test.com"}, format="json")
        assert known.status_code == status.HTTP_200_OK
        assert unknown.status_code == status.HTTP_200_OK
        assert known.json() == unknown.json()

    def test_password_reset_confirm_rejects_bad_token(self, api_client):
        r = api_client.post("/api/v1/auth/password/reset-confirm", {"uid": "abc", "token": "bad", "new_password": "BrandNewPass456!"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_RESET_TOKEN"
