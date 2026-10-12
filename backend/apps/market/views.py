from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import DISCLAIMER

from .providers import SYMBOLS, MarketProviderError, TwelveDataProvider


class MarketSymbolsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"symbols": SYMBOLS})


class MarketQuoteView(APIView):
    def get(self, request):
        symbol = request.query_params.get("symbol", "EUR/USD").upper()
        if symbol not in SYMBOLS:
            return Response({"available": False, "reason": "Unsupported symbol.", "symbols": SYMBOLS})
        if not settings.MARKET_DATA_ENABLED:
            return Response({"available": False, "reason": "Market data is switched off."})
        cache_key = f"market:quote:{symbol}"
        cached = cache.get(cache_key)
        if cached:
            return Response({**cached, "available": True, "is_cached": True, "disclaimer": f"Indicative/delayed data; not for execution. {DISCLAIMER}"})
        try:
            quote = TwelveDataProvider().get_quote(symbol)
        except MarketProviderError as exc:
            return Response({"available": False, "reason": str(exc)})
        cache.set(cache_key, quote, settings.MARKET_CACHE_SECONDS)
        return Response({**quote, "available": True, "is_cached": False, "disclaimer": f"Indicative/delayed data; not for execution. {DISCLAIMER}"})
