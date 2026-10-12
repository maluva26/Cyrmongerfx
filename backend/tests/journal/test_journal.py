from rest_framework import status

from apps.journal.models import JournalEntry


class TestJournal:
    def test_create_and_list(self, trader_client):
        r = trader_client.post("/api/v1/journal", {"notes": "test entry"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        r = trader_client.get("/api/v1/journal")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()) >= 1

    def test_lists_only_own_entries(self, trader_client, user, other_user):
        """TC-11: a trader must only ever see their own journal."""
        JournalEntry.objects.create(user=user, notes="mine")
        JournalEntry.objects.create(user=other_user, notes="theirs")
        r = trader_client.get("/api/v1/journal")
        assert r.status_code == status.HTTP_200_OK
        assert [item["notes"] for item in r.json()] == ["mine"]

    def test_cannot_read_another_users_entry(self, trader_client, other_user):
        entry = JournalEntry.objects.create(user=other_user, notes="secret")
        r = trader_client.get(f"/api/v1/journal/{entry.entry_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_delete_another_users_entry(self, trader_client, other_user):
        entry = JournalEntry.objects.create(user=other_user, notes="secret")
        r = trader_client.delete(f"/api/v1/journal/{entry.entry_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert JournalEntry.objects.filter(entry_id=entry.entry_id).exists()

    def test_update_and_delete_own_entry(self, trader_client, user):
        entry = JournalEntry.objects.create(user=user, notes="before")
        r = trader_client.patch(f"/api/v1/journal/{entry.entry_id}", {"notes": "after"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        entry.refresh_from_db()
        assert entry.notes == "after"

        r = trader_client.delete(f"/api/v1/journal/{entry.entry_id}")
        assert r.status_code == status.HTTP_204_NO_CONTENT
        assert not JournalEntry.objects.filter(entry_id=entry.entry_id).exists()

    def test_cannot_link_another_users_analysis(self, trader_client, other_user):
        from apps.charts.models import Analysis, ChartUpload

        other_chart = ChartUpload.objects.create(user=other_user, mime_type="image/png", size_bytes=10)
        other_analysis = Analysis.objects.create(chart=other_chart, model_version="mock-0.1")
        r = trader_client.post("/api/v1/journal", {"notes": "link", "analysis": str(other_analysis.analysis_id)}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
