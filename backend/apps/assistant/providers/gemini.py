import httpx
from django.conf import settings

from .base import AssistantProviderError, BaseAssistantProvider


class GeminiProvider(BaseAssistantProvider):
    def complete(self, messages: list[dict], system_prompt: str, max_tokens: int) -> str:
        if not settings.GEMINI_API_KEY or not settings.LLM_MODEL:
            raise AssistantProviderError("Assistant is not configured.")
        prompt = system_prompt + "\n\n"
        for message in messages:
            role = "User" if message["role"] == "user" else "Assistant"
            prompt += f"{role}: {message['content']}\n"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent"
        try:
            response = httpx.post(
                url,
                params={"key": settings.GEMINI_API_KEY},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2},
                },
                timeout=10,
            )
            if response.status_code in {429, 403}:
                raise AssistantProviderError("Daily assistant limit reached. Please try again later.")
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except AssistantProviderError:
            raise
        except Exception as exc:
            raise AssistantProviderError("Assistant is unavailable. Please try again later.") from exc
