from unittest.mock import patch

from rest_framework import status


class TestAssistant:
    def test_chat(self, trader_client):
        with patch("apps.assistant.views.get_provider") as mock:
            mock.return_value.complete.return_value = "Educational reply."
            r = trader_client.post("/api/v1/assistant/chat", {"message": "What is a support level?"}, format="json")
            assert r.status_code == status.HTTP_200_OK
            assert r.json()["reply"] == "Educational reply."

    def test_refuses_guarantee(self, trader_client):
        with patch("apps.assistant.views.get_provider") as mock:
            mock.return_value.complete.return_value = "guaranteed profit!"
            r = trader_client.post("/api/v1/assistant/chat", {"message": "Can you guarantee profit?"}, format="json")
            assert r.json()["blocked"] is True

    def test_refuses_risk_free_wording(self, trader_client):
        from apps.assistant.views import filter_reply

        reply, blocked = filter_reply("This is a risk-free profit strategy.")
        assert blocked is True
        assert "guarantees" in reply

    def test_assistant_disabled_returns_503(self, trader_client, settings):
        settings.ASSISTANT_ENABLED = False
        r = trader_client.post("/api/v1/assistant/chat", {"message": "hi"}, format="json")
        assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert r.json()["error"]["code"] == "ASSISTANT_UNAVAILABLE"

    def test_provider_failure_returns_503(self, trader_client):
        from apps.assistant.providers import AssistantProviderError

        with patch("apps.assistant.views.get_provider") as mock:
            mock.return_value.complete.side_effect = AssistantProviderError("upstream down")
            r = trader_client.post("/api/v1/assistant/chat", {"message": "hi"}, format="json")
        assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert r.json()["error"]["code"] == "ASSISTANT_UNAVAILABLE"

    def test_message_is_required(self, trader_client):
        r = trader_client.post("/api/v1/assistant/chat", {}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_unknown_analysis_context_is_404(self, trader_client):
        with patch("apps.assistant.views.get_provider"):
            r = trader_client.post("/api/v1/assistant/chat", {"message": "hi", "analysis_id": "11111111-1111-1111-1111-111111111111"}, format="json")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_conversation_is_created_listed_and_continued(self, trader_client):
        with patch("apps.assistant.views.get_provider") as mock:
            mock.return_value.complete.return_value = "First reply."
            first = trader_client.post("/api/v1/assistant/chat", {"message": "Hello there"}, format="json")
        assert first.status_code == status.HTTP_200_OK
        conversation_id = first.json()["conversation_id"]

        listing = trader_client.get("/api/v1/assistant/conversations")
        assert listing.status_code == status.HTTP_200_OK
        assert len(listing.json()) == 1

        with patch("apps.assistant.views.get_provider") as mock:
            mock.return_value.complete.return_value = "Second reply."
            second = trader_client.post("/api/v1/assistant/chat", {"message": "Follow up", "conversation_id": conversation_id}, format="json")
        assert second.status_code == status.HTTP_200_OK
        assert second.json()["conversation_id"] == conversation_id

        detail = trader_client.get(f"/api/v1/assistant/conversations/{conversation_id}")
        assert detail.status_code == status.HTTP_200_OK
        roles = [message["role"] for message in detail.json()["messages"]]
        assert roles.count("user") == 2
        assert roles.count("assistant") == 2

        deleted = trader_client.delete(f"/api/v1/assistant/conversations/{conversation_id}")
        assert deleted.status_code == status.HTTP_204_NO_CONTENT
        assert trader_client.get(f"/api/v1/assistant/conversations/{conversation_id}").status_code == status.HTTP_404_NOT_FOUND
