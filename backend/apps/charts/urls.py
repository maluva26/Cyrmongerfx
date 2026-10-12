from django.urls import path

from .views import AnalysisDetailView, AnalyzeChartView, ChartDetailView, ChartListView, InternalPurgeView, ModelInfoView

urlpatterns = [
    path("charts/analyze", AnalyzeChartView.as_view(), name="chart-analyze"),
    path("charts", ChartListView.as_view(), name="chart-list"),
    path("charts/<uuid:chart_id>", ChartDetailView.as_view(), name="chart-detail"),
    path("analyses/<uuid:analysis_id>", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("model", ModelInfoView.as_view(), name="model-info"),
    path("internal/purge", InternalPurgeView.as_view(), name="internal-purge"),
]
