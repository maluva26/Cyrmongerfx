class AssistantProviderError(RuntimeError):
    pass


class BaseAssistantProvider:
    def complete(self, messages: list[dict], system_prompt: str, max_tokens: int) -> str:
        raise NotImplementedError
