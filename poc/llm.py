class LLMError(Exception):
    pass


class MockLLMClient:
    """
    Mock LLM для локального poc.

    В целевой системе здесь должен быть LLM gateway:
    - timeout;
    - retry;
    - circuit breaker;
    - cost limit;
    - PII guardrails;
    - prompt injection protection;
    - audit logging.
    """

    def __init__(self, config):
        self.config = config

    def complete(self, prompt: str) -> str:
        if self.config.SIMULATE_LLM_FAILURE:
            raise LLMError("simulated LLM unavailability")

        if "KB_TEXT:" in prompt:
            kb_text = prompt.split("KB_TEXT:", 1)[1].split("\n", 1)[0].strip()
            if kb_text:
                return f"Здравствуйте! {kb_text}"

        return (
            "Здравствуйте! Мы получили ваше обращение. "
            "Оператор ответит в ближайшее время."
        )


class ExternalLLMClient:
    """
    Заглушка внешнего LLM API.

    poc не делает реальных сетевых вызовов.
    """

    def __init__(self, config):
        self.config = config

    def complete(self, prompt: str) -> str:
        raise LLMError("external LLM is not configured in this poc")
