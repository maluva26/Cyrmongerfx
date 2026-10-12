from django.conf import settings
from django.utils import timezone
import httpx


SYMBOLS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/ZAR", "XAU/USD", "AUD/USD", "USD/CHF", "USD/CAD", "NZD/USD"]


class MarketProviderError(RuntimeError):
    pass


class TwelveDataProvider:
    provider = "Twelve Data"

    def get_quote(self, symbol: str) -> dict:
        if not settings.TWELVE_DATA_API_KEY:
            raise MarketProviderError("Market data is not configured.")
        try:
            response = httpx.get(
                "https://api.twelvedata.com/price",
                params={"symbol": symbol, "apikey": settings.TWELVE_DATA_API_KEY},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if "price" not in data:
                raise MarketProviderError(data.get("message", "Market provider returned no price."))
            return {
                "symbol": symbol,
                "price": data["price"],
                "provider": self.provider,
                "retrieved_at_utc": timezone.now().isoformat(),
            }
        except MarketProviderError:
            raise
        except Exception as exc:
            raise MarketProviderError("Market data is unavailable.") from exc
