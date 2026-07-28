import json
import os
import time
from datetime import datetime, timezone

from .classifier import HotPathClassifier
from .config import Config
from .generator import DraftGenerator
from .llm import LLMError
from .models import Decision, Ticket
from .pii import redact_pii
from .retrieval import SimpleRetriever
from .router import Router
from .storage import DecisionStorage


class Orchestrator:
    def __init__(self, config: Config = None):
        self.config = config or Config()

        kb_path = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")
        with open(kb_path, encoding="utf-8") as file:
            docs = json.load(file)

        self.retriever = SimpleRetriever(docs)
        self.classifier = HotPathClassifier()
        self.router = Router()
        self.drafter = DraftGenerator(self.config)
        self.storage = DecisionStorage(self.config.DECISION_LOG_PATH)

    def process(self, ticket: Ticket) -> Decision:
        start = time.perf_counter()

        subject_redacted, subject_pii = redact_pii(ticket.subject)
        body_redacted, body_pii = redact_pii(ticket.body)

        pii_types = sorted(set(subject_pii) | set(body_pii))
        pii_detected = bool(pii_types)

        safe_ticket = Ticket(
            id=ticket.id,
            channel=ticket.channel,
            subject=subject_redacted,
            body=body_redacted,
            user_id=ticket.user_id,
            created_at=ticket.created_at,
        )

        classification = self.classifier.classify(safe_ticket)

        retrieved = self.retriever.search(
            query=f"{subject_redacted}\n{body_redacted}",
            topic=classification.topic,
            top_k=3,
        )

        hot_path_latency_ms = (time.perf_counter() - start) * 1000.0

        route, status, human_required, reasons = self.router.decide(
            classification=classification,
            retrieved=retrieved,
            pii_detected=pii_detected,
            config=self.config,
        )

        reasons = list(reasons)
        reasons.append(f"hot_path_latency_ms={round(hot_path_latency_ms, 2)}")

        if pii_types:
            reasons.append("pii_redacted=" + ",".join(pii_types))

        draft = None
        llm_used = False
        llm_cost_rub = 0.0
        fallback_used = False

        top = retrieved[0] if retrieved else None

        use_llm = (
            route in ("auto_close", "operator_review")
            and classification.risk != "high"
            and not pii_detected
        )

        if use_llm:
            try:
                draft, llm_cost_rub, llm_used = self.drafter.generate(
                    ticket=safe_ticket,
                    classification=classification,
                    retrieved=retrieved,
                )
            except LLMError as exc:
                fallback_used = True
                reasons.append(f"llm_fallback:{exc}")

                draft = self._template_draft(
                    classification=classification,
                    retrieved=retrieved,
                    for_auto=route == "auto_close",
                )

                if route == "auto_close":
                    if top and top.auto_allowed and top.score >= self.config.KB_SCORE_THRESHOLD:
                        status = "auto_closed_template"
                    else:
                        route = "operator_review"
                        status = "llm_fallback_operator"
                        human_required = True
                else:
                    status = "llm_fallback_operator"
        else:
            draft = self._template_draft(
                classification=classification,
                retrieved=retrieved,
                for_auto=route == "auto_close",
            )

            if classification.risk == "high" or pii_detected:
                reasons.append("llm_skipped_high_risk_or_pii")

        if route == "auto_close" and status == "auto_candidate":
            status = "auto_closed"

        decision = Decision(
            ticket_id=ticket.id,
            status=status,
            route=route,
            topic=classification.topic,
            risk=classification.risk,
            confidence=classification.confidence,
            reasons=classification.reasons + reasons,
            retrieved=retrieved,
            draft=draft,
            human_required=human_required,
            pii_detected=pii_detected,
            pii_types=pii_types,
            hot_path_latency_ms=hot_path_latency_ms,
            llm_used=llm_used,
            llm_cost_rub=llm_cost_rub,
            fallback_used=fallback_used,
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_versions={
                "classifier": self.config.MODEL_VERSION_CLASSIFIER,
                "embeddings": self.config.MODEL_VERSION_EMBEDDINGS,
                "llm": self.config.MODEL_VERSION_LLM,
            },
        )

        self.storage.log(decision)
        return decision

    def _template_draft(self, classification, retrieved, for_auto: bool) -> str:
        top = retrieved[0] if retrieved else None

        if for_auto and top and top.auto_allowed and top.score >= self.config.KB_SCORE_THRESHOLD:
            return f"Здравствуйте! {top.text}"

        if top and top.score > 0:
            return (
                "Здравствуйте! Мы получили ваше обращение. "
                f"Предварительная информация: {top.text} "
                "Оператор уточнит детали."
            )

        return "Здравствуйте! Мы получили ваше обращение. Оператор ответит в ближайшее время."
