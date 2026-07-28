import os


class Config:
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
    KB_SCORE_THRESHOLD = float(os.getenv("KB_SCORE_THRESHOLD", "0.20"))
    HOT_PATH_SLO_MS = float(os.getenv("HOT_PATH_SLO_MS", "500"))

    USE_EXTERNAL_LLM = os.getenv("USE_EXTERNAL_LLM", "false").lower() == "true"
    SIMULATE_LLM_FAILURE = os.getenv("SIMULATE_LLM_FAILURE", "false").lower() == "true"

    LLM_DAILY_BUDGET_RUB = float(os.getenv("LLM_DAILY_BUDGET_RUB", "5000"))
    LLM_COST_PER_1K_TOKENS_RUB = float(os.getenv("LLM_COST_PER_1K_TOKENS_RUB", "0.12"))

    DECISION_LOG_PATH = os.getenv(
        "DECISION_LOG_PATH",
        os.path.join("var", "decisions.jsonl"),
    )

    MODEL_VERSION_CLASSIFIER = os.getenv("MODEL_VERSION_CLASSIFIER", "rules-v0.1")
    MODEL_VERSION_EMBEDDINGS = os.getenv("MODEL_VERSION_EMBEDDINGS", "bow-tfidf-v0.1")
    MODEL_VERSION_LLM = os.getenv("MODEL_VERSION_LLM", "mock-llm-v0.1")
