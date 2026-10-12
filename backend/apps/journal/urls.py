from django.urls import path

from .views import JournalDetailView, JournalListView

urlpatterns = [
    path("journal", JournalListView.as_view(), name="journal"),
    path("journal/<uuid:entry_id>", JournalDetailView.as_view(), name="journal-detail"),
]
