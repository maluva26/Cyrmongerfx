from rest_framework import status


class TestFeedback:
    def test_create(self, trader_client):
        r = trader_client.post("/api/v1/feedback", {"type": "OTHER", "message": "Great app"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_admin_list(self, admin_client):
        r = admin_client.get("/api/v1/admin/feedback")
        assert r.status_code == status.HTTP_200_OK

    def test_requires_auth(self, api_client):
        r = api_client.post("/api/v1/feedback", {"type": "OTHER", "message": "hi"}, format="json")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_message_is_required(self, trader_client):
        r = trader_client.post("/api/v1/feedback", {"type": "OTHER"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_reference_another_users_analysis(self, trader_client, other_user):
        from apps.charts.models import Analysis, ChartUpload

        other_chart = ChartUpload.objects.create(user=other_user, mime_type="image/png", size_bytes=10)
        other_analysis = Analysis.objects.create(chart=other_chart, model_version="mock-0.1")

        r = trader_client.post("/api/v1/feedback", {"type": "OTHER", "message": "wrong analysis", "analysis": str(other_analysis.analysis_id)}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_trader_cannot_list_all_feedback(self, trader_client):
        r = trader_client.get("/api/v1/admin/feedback")
        assert r.status_code == status.HTTP_403_FORBIDDEN
