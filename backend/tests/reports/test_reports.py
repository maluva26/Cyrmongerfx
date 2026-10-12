from rest_framework import status

from apps.charts.models import Analysis, ChartUpload
from apps.journal.models import JournalEntry
from apps.learning.models import Lesson


class TestReports:
    def test_dashboard_requires_auth(self, api_client):
        r = api_client.get("/api/v1/dashboard")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_kpis(self, trader_client, user, admin):
        chart = ChartUpload.objects.create(user=user, mime_type="image/png", size_bytes=10)
        Analysis.objects.create(chart=chart, model_version="mock-0.1", status=Analysis.Status.COMPLETED, signal_category=Analysis.Signal.SELL)
        JournalEntry.objects.create(user=user, notes="hello")
        Lesson.objects.create(title="L", category="c", body="b", status=Lesson.Status.PUBLISHED, created_by=admin)

        r = trader_client.get("/api/v1/dashboard")
        assert r.status_code == status.HTTP_200_OK
        body = r.json()
        assert body["kpis"]["lessons_total"] == 1
        assert body["kpis"]["analyses_this_month"] == 1
        assert len(body["recent_analyses"]) == 1
        assert len(body["recent_journal"]) == 1

    def test_activity_report(self, trader_client, user):
        chart = ChartUpload.objects.create(user=user, mime_type="image/png", size_bytes=10)
        Analysis.objects.create(chart=chart, model_version="mock-0.1", status=Analysis.Status.COMPLETED, signal_category=Analysis.Signal.SELL)

        r = trader_client.get("/api/v1/activity")
        assert r.status_code == status.HTTP_200_OK
        body = r.json()
        assert body["journal_entries"] == 0
        assert body["quiz"]["count"] == 0
        assert any(row["signal_category"] == "SELL" for row in body["analyses_by_signal"])

    def test_reports_are_scoped_to_the_current_user(self, trader_client, other_user):
        other_chart = ChartUpload.objects.create(user=other_user, mime_type="image/png", size_bytes=10)
        Analysis.objects.create(chart=other_chart, model_version="mock-0.1", status=Analysis.Status.COMPLETED, signal_category=Analysis.Signal.BUY)
        JournalEntry.objects.create(user=other_user, notes="theirs")

        r = trader_client.get("/api/v1/activity")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["journal_entries"] == 0
        assert r.json()["analyses_by_signal"] == []

    def test_export_csv(self, trader_client):
        r = trader_client.get("/api/v1/activity/export?format=csv")
        assert r.status_code == status.HTTP_200_OK
        assert r["Content-Type"] == "text/csv"
        assert "attachment" in r["Content-Disposition"]

    def test_export_pdf(self, trader_client):
        r = trader_client.get("/api/v1/activity/export?format=pdf")
        assert r.status_code == status.HTTP_200_OK
        assert r["Content-Type"] == "application/pdf"

    def test_export_defaults_to_csv(self, trader_client):
        r = trader_client.get("/api/v1/activity/export")
        assert r["Content-Type"] == "text/csv"
