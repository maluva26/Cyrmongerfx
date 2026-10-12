from rest_framework import status

from apps.core.constants import DISCLAIMER
from apps.risk.models import RiskPlan


class TestRisk:
    def test_calculate_success(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": 1000, "risk_percent": 1, "entry_price": "1.1000", "stop_loss": "1.0900"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert "risk_amount" in r.json()

    def test_zero_balance(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": 0, "risk_percent": 1, "entry_price": "1.1000", "stop_loss": "1.0900"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_entry_equals_stop(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": 1000, "risk_percent": 1, "entry_price": "1.1000", "stop_loss": "1.1000"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "ZERO_PRICE_DISTANCE"

    def test_tp_wrong_side(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": 1000, "risk_percent": 1, "entry_price": "1.1000", "stop_loss": "1.0900", "take_profit": "1.0800"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_TAKE_PROFIT"

    def test_risk_percent_above_limit_rejected(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": 1000, "risk_percent": 99, "entry_price": "1.1000", "stop_loss": "1.0900"}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_RISK_PERCENT"

    def test_long_position_maths(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": "1000", "risk_percent": "1", "entry_price": "1.1000", "stop_loss": "1.0900", "take_profit": "1.1200"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        body = r.json()
        assert body["direction"] == "long"
        assert body["risk_amount"] == 10.0
        assert body["calculated_position_size"] == 1000.0
        assert body["risk_reward_ratio"] == 2.0
        assert body["risk_plan_id"] is None
        assert body["disclaimer"] == DISCLAIMER

    def test_short_position_direction(self, trader_client):
        r = trader_client.post("/api/v1/risk/calculate", {"account_balance": "1000", "risk_percent": "1", "entry_price": "1.1000", "stop_loss": "1.1100"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["direction"] == "short"

    def test_saved_plan_is_listed_and_readable(self, trader_client):
        created = trader_client.post("/api/v1/risk/calculate", {"account_balance": "1000", "risk_percent": "1", "entry_price": "1.1000", "stop_loss": "1.0900", "instrument": "EUR/USD", "save": True}, format="json")
        assert created.status_code == status.HTTP_200_OK
        plan_id = created.json()["risk_plan_id"]
        assert plan_id

        listing = trader_client.get("/api/v1/risk/plans")
        assert listing.status_code == status.HTTP_200_OK
        assert len(listing.json()) == 1

        detail = trader_client.get(f"/api/v1/risk/plans/{plan_id}")
        assert detail.status_code == status.HTTP_200_OK

        deleted = trader_client.delete(f"/api/v1/risk/plans/{plan_id}")
        assert deleted.status_code == status.HTTP_204_NO_CONTENT
        assert not RiskPlan.objects.filter(risk_plan_id=plan_id).exists()

    def test_plan_is_not_visible_to_another_user(self, trader_client, other_user):
        plan = RiskPlan.objects.create(user=other_user, account_balance="1000", risk_percent="1", risk_amount="10", currency="USD")
        assert trader_client.get(f"/api/v1/risk/plans/{plan.risk_plan_id}").status_code == status.HTTP_404_NOT_FOUND
        assert trader_client.get("/api/v1/risk/plans").json() == []
        assert trader_client.delete(f"/api/v1/risk/plans/{plan.risk_plan_id}").status_code == status.HTTP_404_NOT_FOUND
        assert RiskPlan.objects.filter(risk_plan_id=plan.risk_plan_id).exists()
