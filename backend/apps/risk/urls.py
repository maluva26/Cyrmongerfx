from django.urls import path

from .views import RiskCalculateView, RiskPlanDetailView, RiskPlanListView

urlpatterns = [
    path("risk/calculate", RiskCalculateView.as_view(), name="risk-calculate"),
    path("risk/plans", RiskPlanListView.as_view(), name="risk-plans"),
    path("risk/plans/<uuid:risk_plan_id>", RiskPlanDetailView.as_view(), name="risk-plan-detail"),
]
