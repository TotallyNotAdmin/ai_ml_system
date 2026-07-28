from .llm import ExternalLLMClient, LLMError, MockLLMClient
from .models import Classification, RetrievedDoc, Ticket
from typing import List


class DraftGenerator:
    def __init__(self, config, client=None):
        self.config = config
        self.spent_today = 0.0

        if client is not None:
            self.client = client
        elif config.USE_EXTERNAL_LLM:
            self.client = ExternalLLMClient(config)
        else:
            self.client = MockLLMClient(config)

    def generate(
        self,
        ticket: Ticket,
        classification: Classification,
        retrieved: List[RetrievedDoc],
    ):
        prompt = self._build_prompt(ticket, classification, retrieved)
        tokens = self._estimate_tokens(prompt)
        cost = round(tokens / 1000.0 * self.config.LLM_COST_PER_1K_TOKENS_RUB, 6)

        if self.spent_today + cost > self.config.LLM_DAILY_BUDGET_RUB:
            raise LLMError("daily LLM budget exceeded")

        text = self.client.complete(prompt)
        self.spent_today += cost

        return text, cost, True

    def _build_prompt(
        self,
        ticket: Ticket,
        classification: Classification,
        retrieved: List[RetrievedDoc],
    ) -> str:
        top = retrieved[0] if retrieved else None

        lines = [
            "TASK: Draft a short support answer in Russian.",
            "POLICY: Do not include PII.",
            "POLICY: Do not promise refunds, compensations or account changes.",
            "POLICY: If unsure, ask operator to review.",
            f"TOPIC: {classification.topic}",
            f"RISK: {classification.risk}",
            f"SUBJECT: {ticket.subject}",
            f"BODY: {ticket.body}",
        ]

        if top:
            lines.extend(
                [
                    f"KB_ID: {top.id}",
                    f"KB_TEXT: {top.text}",
                ]
            )

        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) // 4))
