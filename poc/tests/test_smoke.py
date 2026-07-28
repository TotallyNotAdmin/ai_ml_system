import tempfile
import unittest

from poc.config import Config
from poc.models import Ticket
from poc.orchestrator import Orchestrator


def make_orchestrator(**overrides):
    config = Config()
    config.DECISION_LOG_PATH = tempfile.mktemp(suffix=".jsonl")
    config.KB_SCORE_THRESHOLD = 0.05

    for key, value in overrides.items():
        setattr(config, key, value)

    return Orchestrator(config), config


class SmokeTest(unittest.TestCase):
    def test_happy_path_auto_close(self):
        orchestrator, config = make_orchestrator()

        ticket = Ticket(
            id="T-TEST-001",
            channel="chat",
            subject="Отмена подписки",
            body="Как отменить подписку?",
        )

        decision = orchestrator.process(ticket)

        self.assertEqual(decision.route, "auto_close")
        self.assertFalse(decision.human_required)
        self.assertIsNotNone(decision.draft)
        self.assertLess(decision.hot_path_latency_ms, config.HOT_PATH_SLO_MS)

    def test_risky_payment_with_pii_goes_to_operator(self):
        orchestrator, _ = make_orchestrator()

        ticket = Ticket(
            id="T-TEST-002",
            channel="email",
            subject="Списание денег",
            body=(
                "С карты списали деньги, карта 4111 1111 1111 1111, "
                "почта user@example.com"
            ),
        )

        decision = orchestrator.process(ticket)

        self.assertTrue(decision.pii_detected)
        self.assertIn("card", decision.pii_types)
        self.assertIn("email", decision.pii_types)
        self.assertEqual(decision.route, "urgent_operator")
        self.assertTrue(decision.human_required)
        self.assertNotIn("4111", decision.draft or "")
        self.assertNotIn("user@example.com", decision.draft or "")

    def test_low_confidence_goes_to_operator(self):
        orchestrator, _ = make_orchestrator()

        ticket = Ticket(
            id="T-TEST-003",
            channel="web",
            subject="Странный вопрос",
            body="Фиолетовые бегемоты умеют летать?",
        )

        decision = orchestrator.process(ticket)

        self.assertEqual(decision.topic, "unknown")
        self.assertTrue(decision.human_required)
        self.assertEqual(decision.route, "operator_review")

    def test_llm_failure_fallback(self):
        orchestrator, _ = make_orchestrator(SIMULATE_LLM_FAILURE=True)

        ticket = Ticket(
            id="T-TEST-004",
            channel="chat",
            subject="Отмена подписки",
            body="Как отменить подписку?",
        )

        decision = orchestrator.process(ticket)

        self.assertTrue(decision.fallback_used)
        self.assertFalse(decision.llm_used)
        self.assertIsNotNone(decision.draft)
        self.assertIn(decision.route, ("auto_close", "operator_review"))


if __name__ == "__main__":
    unittest.main()
