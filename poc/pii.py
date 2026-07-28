import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

CARD_RE = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b")

PHONE_RE = re.compile(
    r"(?:\+7|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-()]*\d{2}[\s\-()]*\d{2}"
)

CVV_RE = re.compile(r"\b(?:cvv|cvc)\b", re.IGNORECASE)


def redact_pii(text: str):
    """
    Упрощённый PII redactor для poc.

    В production нужно использовать:
    - более строгие regex;
    - NER;
    - DLP-политики;
    - словари идентификаторов;
    - проверку перед отправкой в LLM и логи.
    """
    found = set()

    if EMAIL_RE.search(text):
        found.add("email")
        text = EMAIL_RE.sub("[EMAIL]", text)

    if CARD_RE.search(text):
        found.add("card")
        text = CARD_RE.sub("[CARD]", text)

    if PHONE_RE.search(text):
        found.add("phone")
        text = PHONE_RE.sub("[PHONE]", text)

    if CVV_RE.search(text):
        found.add("cvv")
        text = CVV_RE.sub("[CVV]", text)

    return text, sorted(found)
