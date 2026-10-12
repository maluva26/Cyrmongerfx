from django.urls import path

from .views import CommunityMessageListCreateView

urlpatterns = [
    path("community/messages", CommunityMessageListCreateView.as_view(), name="community-messages"),
]
