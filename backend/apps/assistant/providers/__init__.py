from django.conf import settings

from .anthropic_provider import AnthropicProvider
from .base import AssistantProviderError
from .gemini import GeminiProvider


def get_provider():
    provider = settings.LLM_PROVIDER.lower()
    if provider == "anthropic":
        return AnthropicProvider()
    return GeminiProvider()


__all__ = ["AssistantProviderError", "get_provider"]
