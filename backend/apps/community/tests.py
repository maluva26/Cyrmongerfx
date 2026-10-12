from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.community.models import CommunityMessage


class CommunityMessageApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="trader@example.com",
            password="temporary-pass-123",
            full_name="Test Trader",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_messages_includes_demo_messages(self):
        response = self.client.get("/api/v1/community/messages")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_create_text_message(self):
        response = self.client.post("/api/v1/community/messages", {"body": "Hello traders"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["body"], "Hello traders")
        self.assertTrue(CommunityMessage.objects.filter(user=self.user, body="Hello traders").exists())

    def test_rejects_empty_message(self):
        response = self.client.post("/api/v1/community/messages", {"body": ""}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
