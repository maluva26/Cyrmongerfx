from rest_framework import serializers

from .models import RiskPlan


class RiskPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskPlan
        fields = "__all__"
        read_only_fields = ["risk_plan_id", "user", "risk_amount", "calculated_position_size", "risk_reward_ratio", "created_at"]


class RiskCalculateSerializer(serializers.Serializer):
    account_balance = serializers.DecimalField(max_digits=18, decimal_places=4)
    risk_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    instrument = serializers.CharField(max_length=40, required=False, allow_blank=True)
    entry_price = serializers.DecimalField(max_digits=18, decimal_places=8)
    stop_loss = serializers.DecimalField(max_digits=18, decimal_places=8)
    take_profit = serializers.DecimalField(max_digits=18, decimal_places=8, required=False)
    currency = serializers.CharField(max_length=10, default="USD")
    save = serializers.BooleanField(default=False)
