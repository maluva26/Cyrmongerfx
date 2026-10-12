import uuid

from django.conf import settings
from django.db import models


class RiskPlan(models.Model):
    risk_plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_plans")
    account_balance = models.DecimalField(max_digits=18, decimal_places=4)
    risk_percent = models.DecimalField(max_digits=5, decimal_places=2)
    instrument = models.CharField(max_length=40, blank=True, null=True)
    entry_price = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    risk_amount = models.DecimalField(max_digits=18, decimal_places=4)
    calculated_position_size = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    risk_reward_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "risk_plan"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]
