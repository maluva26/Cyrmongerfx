from rest_framework import status


class TestSecurity:
    def test_unauthenticated_401(self, api_client):
        r = api_client.get("/api/v1/dashboard")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_idor_chart(self, api_client, user, other_user):
        from apps.charts.models import ChartUpload

        chart = ChartUpload.objects.create(user=user, mime_type="image/png", size_bytes=10)
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(other_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
        r = api_client.get(f"/api/v1/charts/{chart.chart_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_trader_cannot_admin(self, api_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
        r = api_client.get("/api/v1/admin/lessons")
        assert r.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_endpoints_return_401(self, api_client):
        paths = [
            "/api/v1/me",
            "/api/v1/dashboard",
            "/api/v1/charts",
            "/api/v1/journal",
            "/api/v1/lessons",
            "/api/v1/progress",
            "/api/v1/risk/plans",
            "/api/v1/assistant/conversations",
            "/api/v1/activity",
        ]
        for path in paths:
            assert api_client.get(path).status_code == status.HTTP_401_UNAUTHORIZED, path

    def test_admin_endpoints_reject_trader(self, trader_client):
        paths = ["/api/v1/admin/lessons", "/api/v1/admin/feedback", "/api/v1/admin/status"]
        for path in paths:
            assert trader_client.get(path).status_code == status.HTTP_403_FORBIDDEN, path

    def test_idor_analysis(self, trader_client, other_user):
        from apps.charts.models import Analysis, ChartUpload

        chart = ChartUpload.objects.create(user=other_user, mime_type="image/png", size_bytes=10)
        analysis = Analysis.objects.create(chart=chart, model_version="mock-0.1")
        r = trader_client.get(f"/api/v1/analyses/{analysis.analysis_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_idor_assistant_conversation(self, trader_client, other_user):
        from apps.assistant.models import AssistantConversation

        conversation = AssistantConversation.objects.create(user=other_user, title="private")
        r = trader_client.get(f"/api/v1/assistant/conversations/{conversation.conversation_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_action_is_audited(self, admin_client, admin):
        """SEC-07: privileged mutations must leave an audit trail."""
        from apps.core.models import AuditLog

        r = admin_client.post("/api/v1/admin/lessons", {"title": "Audited", "category": "test", "body": "body"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        entry = AuditLog.objects.filter(action="lesson.create").first()
        assert entry is not None
        assert entry.actor_id == admin.pk
        assert entry.object_type == "Lesson"

    def test_login_is_audited(self, api_client, user):
        from apps.core.models import AuditLog

        api_client.post("/api/v1/auth/login", {"email": "user@test.com", "password": "TestPass123!"}, format="json")
        assert AuditLog.objects.filter(action="auth.login").exists()

    def test_internal_purge_is_hidden_without_cron_token(self, api_client):
        r = api_client.post("/api/v1/internal/purge")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_internal_purge_removes_expired_charts_with_token(self, api_client, settings, user):
        from datetime import timedelta

        from django.utils import timezone

        from apps.charts.models import ChartUpload

        settings.INTERNAL_CRON_TOKEN = "cron-secret"
        expired = ChartUpload.objects.create(user=user, mime_type="image/png", size_bytes=10, retention_until=timezone.now() - timedelta(days=1))

        r = api_client.post("/api/v1/internal/purge", HTTP_X_INTERNAL_CRON_TOKEN="cron-secret")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["removed"] == 1
        expired.refresh_from_db()
        assert expired.status == ChartUpload.Status.REMOVED
        assert expired.storage_ref is None
