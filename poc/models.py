from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Ticket:
    id: str
    channel: str
    subject: str
    body: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class RetrievedDoc:
    id: str
    title: str
    text: str
    score: float
    topic: str
    auto_allowed: bool


@dataclass
class Classification:
    topic: str
    risk: str
    confidence: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class Decision:
    ticket_id: str
    status: str
    route: str
    topic: str
    risk: str
    confidence: float
    reasons: List[str]
    retrieved: List[RetrievedDoc]
    draft: Optional[str]
    human_required: bool
    pii_detected: bool
    pii_types: List[str]
    hot_path_latency_ms: float
    llm_used: bool
    llm_cost_rub: float
    fallback_used: bool
    timestamp: str
    model_versions: Dict[str, str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "route": self.route,
            "topic": self.topic,
            "risk": self.risk,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "retrieved": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "score": round(doc.score, 4),
                    "topic": doc.topic,
                    "auto_allowed": doc.auto_allowed,
                }
                for doc in self.retrieved
            ],
            "draft": self.draft,
            "human_required": self.human_required,
            "pii_detected": self.pii_detected,
            "pii_types": self.pii_types,
            "hot_path_latency_ms": round(self.hot_path_latency_ms, 2),
            "llm_used": self.llm_used,
            "llm_cost_rub": self.llm_cost_rub,
            "fallback_used": self.fallback_used,
            "model_versions": self.model_versions,
        }
