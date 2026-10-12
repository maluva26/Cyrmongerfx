from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.responses import error_response

from .models import JournalEntry
from .serializers import JournalEntrySerializer


class JournalListView(APIView):
    def get(self, request):
        return Response(JournalEntrySerializer(JournalEntry.objects.filter(user=request.user), many=True, context={"request": request}).data)

    def post(self, request):
        serializer = JournalEntrySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        entry = serializer.save(user=request.user)
        return Response(JournalEntrySerializer(entry, context={"request": request}).data, status=status.HTTP_201_CREATED)


class JournalDetailView(APIView):
    def get_object(self, request, entry_id):
        return JournalEntry.objects.filter(user=request.user, entry_id=entry_id).first()

    def get(self, request, entry_id):
        entry = self.get_object(request, entry_id)
        if not entry:
            return error_response("NOT_FOUND", "Journal entry not found.", status.HTTP_404_NOT_FOUND)
        return Response(JournalEntrySerializer(entry, context={"request": request}).data)

    def patch(self, request, entry_id):
        entry = self.get_object(request, entry_id)
        if not entry:
            return error_response("NOT_FOUND", "Journal entry not found.", status.HTTP_404_NOT_FOUND)
        serializer = JournalEntrySerializer(entry, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, entry_id):
        entry = self.get_object(request, entry_id)
        if not entry:
            return error_response("NOT_FOUND", "Journal entry not found.", status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
