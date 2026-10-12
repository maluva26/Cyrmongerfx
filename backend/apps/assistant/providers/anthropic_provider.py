from django.conf import settings

from .base import AssistantProviderError, BaseAssistantProvider


class AnthropicProvider(BaseAssistantProvider):
    def complete(self, messages: list[dict], system_prompt: str, max_tokens: int) -> str:
        if not settings.ANTHROPIC_API_KEY or not settings.LLM_MODEL:
            raise AssistantProviderError("Assistant is not configured.")
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=10)
            result = client.messages.create(
                model=settings.LLM_MODEL,
                system=system_prompt,
                max_tokens=max_tokens,
                messages=messages,  # type: ignore[arg-type]
            )
            content = result.content[0]
            if hasattr(content, "text"):
                return content.text
            raise AssistantProviderError("Assistant returned an unexpected response.")
        except AssistantProviderError:
            raise
        except Exception as exc:
            raise AssistantProviderError("Assistant is unavailable. Please try again later.") from exc
