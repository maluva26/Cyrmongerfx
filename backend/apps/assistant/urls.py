from django.urls import path

from .views import AssistantChatView, AssistantConversationDetailView, AssistantConversationListView

urlpatterns = [
    path("assistant/chat", AssistantChatView.as_view(), name="assistant-chat"),
    path("assistant/conversations", AssistantConversationListView.as_view(), name="assistant-conversations"),
    path("assistant/conversations/<uuid:conversation_id>", AssistantConversationDetailView.as_view(), name="assistant-conversation"),
]
