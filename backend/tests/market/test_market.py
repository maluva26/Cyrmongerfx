from unittest.mock import patch

from rest_framework import status

from apps.market.providers import MarketProviderError


class TestMarket:
    def test_disabled(self, trader_client, settings):
        settings.MARKET_DATA_ENABLED = False
        r = trader_client.get("/api/v1/market/quote?symbol=EUR/USD")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["available"] is False

    def test_unsupported_symbol(self, trader_client):
        r = trader_client.get("/api/v1/market/quote?symbol=BAD/SYM")
        assert r.json()["available"] is False

    def test_symbols_public(self, client):
        r = client.get("/api/v1/market/symbols")
        assert r.status_code == status.HTTP_200_OK
        assert "EUR/USD" in r.json()["symbols"]

    def test_provider_down_reports_unavailable(self, trader_client, settings):
        """TC-10: a provider failure must degrade to available=false, never a 500."""
        settings.MARKET_DATA_ENABLED = True
        with patch("apps.market.views.TwelveDataProvider") as mock:
            mock.return_value.get_quote.side_effect = MarketProviderError("Market data is unavailable.")
            r = trader_client.get("/api/v1/market/quote?symbol=EUR/USD")
        assert r.status_code == status.HTTP_200_OK
        body = r.json()
        assert body["available"] is False
        assert body["reason"] == "Market data is unavailable."

    def test_quote_success_then_cached(self, trader_client, settings):
        settings.MARKET_DATA_ENABLED = True
        quote = {"symbol": "EUR/USD", "price": "1.0850", "provider": "Twelve Data", "retrieved_at_utc": "2026-10-07T00:00:00+00:00"}
        with patch("apps.market.views.TwelveDataProvider") as mock:
            mock.return_value.get_quote.return_value = quote
            first = trader_client.get("/api/v1/market/quote?symbol=EUR/USD")
            second = trader_client.get("/api/v1/market/quote?symbol=EUR/USD")
        assert first.status_code == status.HTTP_200_OK
        assert first.json()["available"] is True
        assert first.json()["is_cached"] is False
        assert second.json()["is_cached"] is True
        assert "disclaimer" in first.json()
        assert mock.return_value.get_quote.call_count == 1
