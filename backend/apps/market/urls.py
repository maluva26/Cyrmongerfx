from django.urls import path

from .views import MarketQuoteView, MarketSymbolsView

urlpatterns = [
    path("market/quote", MarketQuoteView.as_view(), name="market-quote"),
    path("market/symbols", MarketSymbolsView.as_view(), name="market-symbols"),
]
