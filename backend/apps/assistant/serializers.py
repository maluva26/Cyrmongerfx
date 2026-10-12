from rest_framework import serializers

from .models import AssistantConversation, AssistantMessage


class AssistantChatSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False)
    message = serializers.CharField(max_length=1500)
    analysis_id = serializers.UUIDField(required=False)


class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = ["message_id", "role", "content", "blocked", "created_at"]


class AssistantConversationSerializer(serializers.ModelSerializer):
    messages = AssistantMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AssistantConversation
        fields = ["conversation_id", "title", "created_at", "messages"]
