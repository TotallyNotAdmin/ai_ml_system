import json
import os

from .config import Config
from .models import Ticket
from .orchestrator import Orchestrator


def main() -> None:
    config = Config()
    orchestrator = Orchestrator(config)

    data_path = os.path.join(os.path.dirname(__file__), "data", "mock_tickets.json")

    with open(data_path, encoding="utf-8") as file:
        raw_tickets = json.load(file)

    tickets = [Ticket(**item) for item in raw_tickets]

    print("Support Ticket AI Triage poc")
    print("=" * 80)

    for ticket in tickets:
        decision = orchestrator.process(ticket)

        print("-" * 80)
        print(f"Ticket: {decision.ticket_id}")
        print(f"Topic: {decision.topic}")
        print(f"Risk: {decision.risk}")
        print(f"Confidence: {decision.confidence}")
        print(f"Route: {decision.route}")
        print(f"Status: {decision.status}")
        print(f"Human required: {decision.human_required}")
        print(f"PII detected: {decision.pii_detected} {decision.pii_types}")
        print(f"Hot path latency: {round(decision.hot_path_latency_ms, 2)} ms")
        print(f"LLM used: {decision.llm_used}")
        print(f"LLM cost: {decision.llm_cost_rub} RUB")
        print(f"Fallback used: {decision.fallback_used}")
        print(f"Draft: {decision.draft}")

    print("-" * 80)
    print(f"Decision log: {config.DECISION_LOG_PATH}")


if __name__ == "__main__":
    main()
