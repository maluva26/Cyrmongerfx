from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import DISCLAIMER
from apps.core.responses import error_response

from .models import RiskPlan
from .serializers import RiskCalculateSerializer, RiskPlanSerializer


def calculate(payload):
    balance = payload["account_balance"]
    risk_percent = payload["risk_percent"]
    entry = payload["entry_price"]
    stop = payload["stop_loss"]
    take_profit = payload.get("take_profit")
    if balance <= 0:
        return "INVALID_BALANCE", "Account balance must be greater than zero.", None
    if risk_percent <= 0 or risk_percent > Decimal(settings.MAX_RISK_PERCENT):
        return "INVALID_RISK_PERCENT", f"Risk percent must be greater than zero and at most {settings.MAX_RISK_PERCENT}%.", None
    if entry <= 0 or stop <= 0:
        return "INVALID_PRICE", "Entry and stop-loss must be greater than zero.", None
    if entry == stop:
        return "ZERO_PRICE_DISTANCE", "Entry and stop-loss cannot be the same price.", None
    direction = "long" if stop < entry else "short"
    if take_profit is not None:
        if (direction == "long" and take_profit <= entry) or (direction == "short" and take_profit >= entry):
            return "INVALID_TAKE_PROFIT", "Take-profit must be on the profitable side of entry.", None
    risk_amount = balance * risk_percent / Decimal("100")
    distance = abs(entry - stop)
    position_size = risk_amount / distance
    risk_reward = abs(take_profit - entry) / distance if take_profit is not None else None
    return (
        None,
        None,
        {
            "risk_amount": risk_amount.quantize(Decimal("0.0001")),
            "calculated_position_size": position_size.quantize(Decimal("0.00000001")),
            "risk_reward_ratio": risk_reward.quantize(Decimal("0.0001")) if risk_reward is not None else None,
            "direction": direction,
        },
    )


class RiskCalculateView(APIView):
    def post(self, request):
        serializer = RiskCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code, message, result = calculate(serializer.validated_data)
        if code:
            return error_response(code, message, status.HTTP_400_BAD_REQUEST)
        plan = None
        if serializer.validated_data["save"]:
            plan = RiskPlan.objects.create(
                user=request.user,
                account_balance=serializer.validated_data["account_balance"],
                risk_percent=serializer.validated_data["risk_percent"],
                instrument=serializer.validated_data.get("instrument") or None,
                entry_price=serializer.validated_data["entry_price"],
                stop_loss=serializer.validated_data["stop_loss"],
                take_profit=serializer.validated_data.get("take_profit"),
                risk_amount=result["risk_amount"],
                calculated_position_size=result["calculated_position_size"],
                risk_reward_ratio=result["risk_reward_ratio"],
                currency=serializer.validated_data["currency"],
            )
        return Response(
            {
                **result,
                "risk_plan_id": plan.risk_plan_id if plan else None,
                "assumptions": "Position size is units of the instrument per 1 unit price move; convert to lots using your broker contract size. This is not a trade order.",
                "disclaimer": DISCLAIMER,
            }
        )


class RiskPlanListView(APIView):
    def get(self, request):
        return Response(RiskPlanSerializer(RiskPlan.objects.filter(user=request.user), many=True).data)


class RiskPlanDetailView(APIView):
    def get_object(self, request, risk_plan_id):
        return RiskPlan.objects.filter(user=request.user, risk_plan_id=risk_plan_id).first()

    def get(self, request, risk_plan_id):
        plan = self.get_object(request, risk_plan_id)
        if not plan:
            return error_response("NOT_FOUND", "Risk plan not found.", status.HTTP_404_NOT_FOUND)
        return Response(RiskPlanSerializer(plan).data)

    def delete(self, request, risk_plan_id):
        plan = self.get_object(request, risk_plan_id)
        if not plan:
            return error_response("NOT_FOUND", "Risk plan not found.", status.HTTP_404_NOT_FOUND)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
