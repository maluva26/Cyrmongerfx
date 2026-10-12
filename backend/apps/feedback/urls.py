from django.urls import path

from .views import AdminFeedbackListView, FeedbackCreateView

urlpatterns = [
    path("feedback", FeedbackCreateView.as_view(), name="feedback"),
    path("admin/feedback", AdminFeedbackListView.as_view(), name="admin-feedback"),
]
