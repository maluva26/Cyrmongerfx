from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole

from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackCreateView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "feedback"

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save(user=request.user)
        return Response(FeedbackSerializer(feedback, context={"request": request}).data, status=status.HTTP_201_CREATED)


class AdminFeedbackListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(FeedbackSerializer(Feedback.objects.all(), many=True, context={"request": request}).data)
