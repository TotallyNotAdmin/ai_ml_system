from .models import Classification, Ticket

TOPIC_KEYWORDS = {
    "subscription": [
        "подписк",
        "отменить",
        "продление",
        "тариф",
        "план",
        "subscription",
        "cancel",
    ],
    "payment": [
        "оплат",
        "платеж",
        "платёж",
        "карт",
        "списал",
        "списан",
        "деньг",
        "payment",
        "card",
        "charge",
        "billing",
        "счет",
        "счёт",
        "возврат",
        "refund",
    ],
    "security": [
        "взлом",
        "украли",
        "мошен",
        "пароль",
        "доступ",
        "security",
        "hack",
        "угроз",
        "подозрит",
    ],
    "outage": [
        "не работает",
        "недоступен",
        "сбой",
        "ошибк",
        "error",
        "500",
        "упал",
        "не открывается",
        "не запускается",
        "не грузит",
    ],
    "account": [
        "аккаунт",
        "профиль",
        "регистрац",
        "восстановить",
        "почта",
        "email",
    ],
}

PAYMENT_HIGH_KEYWORDS = [
    "списал",
    "списан",
    "деньг",
    "карт",
    "card",
    "charge",
    "возврат",
    "refund",
    "платеж",
    "платёж",
]


class HotPathClassifier:
    """
    Очень простой rule-based классификатор для poc.

    В целевой системе:
    - topic: лёгкая ML-модель или fine-tuned small transformer;
    - risk: правила + ML risk score;
    - confidence: calibrated probability.
    """

    def classify(self, ticket: Ticket) -> Classification:
        text = f"{ticket.subject}\n{ticket.body}".lower()
        subject = ticket.subject.lower()

        scores = {}
        matches = {}

        for topic, keywords in TOPIC_KEYWORDS.items():
            score = 0
            matched = []

            for keyword in keywords:
                count = text.count(keyword)
                if count > 0:
                    score += count
                    matched.append(keyword)

                    if keyword in subject:
                        score += 1

            scores[topic] = score
            matches[topic] = matched

        max_topic = max(scores, key=scores.get)
        max_score = scores[max_topic]

        if max_score == 0:
            return Classification(
                topic="unknown",
                risk="medium",
                confidence=0.10,
                reasons=["no_keyword_match"],
            )

        total_score = sum(scores.values()) or 1
        confidence = min(
            0.95,
            0.35 + 0.18 * max_score + 0.15 * (max_score / total_score),
        )

        risk = self._assess_risk(max_topic, text)

        reasons = [
            f"classifier_topic={max_topic}",
            f"max_score={max_score}",
            f"matched={','.join(matches[max_topic][:5]) or 'n/a'}",
        ]

        return Classification(
            topic=max_topic,
            risk=risk,
            confidence=round(confidence, 3),
            reasons=reasons,
        )

    def _assess_risk(self, topic: str, text: str) -> str:
        if topic == "security":
            return "high"

        if topic == "payment":
            return "high" if any(keyword in text for keyword in PAYMENT_HIGH_KEYWORDS) else "medium"

        if topic == "subscription":
            if any(keyword in text for keyword in PAYMENT_HIGH_KEYWORDS):
                return "high"
            if any(keyword in text for keyword in ["отменить", "как", "настроить", "продление", "тариф", "план"]):
                return "low"
            return "medium"

        if topic == "outage":
            if any(keyword in text for keyword in ["массов", "лежит", "всё упало", "все упало"]):
                return "high"
            return "medium"

        if topic == "account":
            if any(keyword in text for keyword in ["пароль", "доступ"]):
                return "medium"
            return "low"

        return "low"
