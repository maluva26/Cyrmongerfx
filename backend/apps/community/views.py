from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsTrader

from .models import CommunityMessage
from .serializers import CommunityMessageCreateSerializer, CommunityMessageSerializer


class CommunityMessageListCreateView(APIView):
    permission_classes = [IsTrader]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        queryset = CommunityMessage.objects.select_related("user").all()[:80]
        messages = list(reversed(queryset))
        return Response(CommunityMessageSerializer(messages, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = CommunityMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        author_name = request.user.full_name.strip() if request.user.full_name else request.user.email.split("@")[0]
        message = serializer.save(user=request.user, author_name=author_name)
        return Response(CommunityMessageSerializer(message, context={"request": request}).data, status=status.HTTP_201_CREATED)
