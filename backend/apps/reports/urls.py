from django.urls import path

from .views import ActivityReportView, DashboardView, ExportReportView

urlpatterns = [
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("activity", ActivityReportView.as_view(), name="activity"),
    path("activity/export", ExportReportView.as_view(), name="activity-export"),
]
