from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.charts.models import Analysis
from apps.core.constants import DISCLAIMER
from apps.core.responses import error_response

from .models import AssistantConversation, AssistantMessage
from .prompts import SYSTEM_PROMPT
from .providers import AssistantProviderError, get_provider
from .serializers import AssistantChatSerializer, AssistantConversationSerializer

BLOCKED_PHRASES = ["guaranteed profit", "can't lose", "100% sure", "risk-free profit"]


def filter_reply(reply: str) -> tuple[str, bool]:
    lowered = reply.lower()
    if any(phrase in lowered for phrase in BLOCKED_PHRASES):
        return (
            "I cannot make guarantees or present trading as risk-free. Use this platform for education only, and remember that Forex trading carries a high risk of loss.",
            True,
        )
    return reply, False


class AssistantChatView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "assistant"

    def post(self, request):
        if not settings.ASSISTANT_ENABLED:
            return error_response("ASSISTANT_UNAVAILABLE", "Assistant is currently switched off.", status.HTTP_503_SERVICE_UNAVAILABLE)
        serializer = AssistantChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation_id = serializer.validated_data.get("conversation_id")
        if conversation_id:
            conversation = AssistantConversation.objects.filter(user=request.user, conversation_id=conversation_id).first()
            if not conversation:
                return error_response("NOT_FOUND", "Conversation not found.", status.HTTP_404_NOT_FOUND)
        else:
            title = serializer.validated_data["message"][:80]
            conversation = AssistantConversation.objects.create(user=request.user, title=title)

        user_message = serializer.validated_data["message"]
        analysis_id = serializer.validated_data.get("analysis_id")
        if analysis_id:
            analysis = Analysis.objects.filter(analysis_id=analysis_id, chart__user=request.user).first()
            if not analysis:
                return error_response("NOT_FOUND", "Analysis not found.", status.HTTP_404_NOT_FOUND)
            labels = ", ".join(d.label for d in analysis.detections.all()) or "no detections"
            user_message += f"\n\nContext from platform analysis: signal={analysis.signal_category}, model_score={analysis.overall_confidence}, labels={labels}."
        AssistantMessage.objects.create(conversation=conversation, role=AssistantMessage.Role.USER, content=serializer.validated_data["message"])
        context = list(conversation.messages.order_by("-created_at")[:10])
        messages = [{"role": item.role, "content": item.content} for item in reversed(context)]
        messages.append({"role": "user", "content": user_message})
        try:
            reply = get_provider().complete(messages, SYSTEM_PROMPT, settings.ASSISTANT_MAX_TOKENS)
        except AssistantProviderError as exc:
            return error_response("ASSISTANT_UNAVAILABLE", str(exc), status.HTTP_503_SERVICE_UNAVAILABLE)
        reply, blocked = filter_reply(reply)
        AssistantMessage.objects.create(conversation=conversation, role=AssistantMessage.Role.ASSISTANT, content=reply, blocked=blocked)
        return Response({"conversation_id": conversation.conversation_id, "reply": reply, "blocked": blocked, "disclaimer": DISCLAIMER})


class AssistantConversationListView(APIView):
    def get(self, request):
        conversations = AssistantConversation.objects.filter(user=request.user)
        return Response(AssistantConversationSerializer(conversations, many=True).data)


class AssistantConversationDetailView(APIView):
    def get_object(self, request, conversation_id):
        return AssistantConversation.objects.filter(user=request.user, conversation_id=conversation_id).first()

    def get(self, request, conversation_id):
        conversation = self.get_object(request, conversation_id)
        if not conversation:
            return error_response("NOT_FOUND", "Conversation not found.", status.HTTP_404_NOT_FOUND)
        return Response(AssistantConversationSerializer(conversation).data)

    def delete(self, request, conversation_id):
        conversation = self.get_object(request, conversation_id)
        if not conversation:
            return error_response("NOT_FOUND", "Conversation not found.", status.HTTP_404_NOT_FOUND)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
