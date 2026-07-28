from .config import Config
from .models import Classification, RetrievedDoc
from typing import List, Tuple


class Router:
    """
    Детерминированный router.

    В poc правила простые.
    В production:
    - calibrated thresholds;
    - incident mode;
    - business rules;
    - A/B testing;
    - audit of routing decisions.
    """

    def decide(
        self,
        classification: Classification,
        retrieved: List[RetrievedDoc],
        pii_detected: bool,
        config: Config,
    ) -> Tuple[str, str, bool, List[str]]:
        reasons = []

        top = retrieved[0] if retrieved else None
        kb_score = top.score if top else 0.0
        kb_auto_allowed = top.auto_allowed if top else False

        if classification.risk == "high" or pii_detected:
            route = "urgent_operator" if classification.risk == "high" else "operator_review"
            status = "risky_or_pii"
            reasons.append("high_risk_or_pii")
            return route, status, True, reasons

        if classification.topic == "unknown" or classification.confidence < config.CONFIDENCE_THRESHOLD:
            reasons.append("low_confidence_or_unknown")
            return "operator_review", "low_confidence", True, reasons

        if (
            classification.risk == "low"
            and kb_auto_allowed
            and kb_score >= config.KB_SCORE_THRESHOLD
        ):
            reasons.append("low_risk_kb_match")
            return "auto_close", "auto_candidate", False, reasons

        reasons.append("needs_human_review")
        return "operator_review", "needs_review", True, reasons
