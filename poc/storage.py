import json
import os

from .models import Decision


class DecisionStorage:
    """
    Минимальный audit log в JSONL.

    В production:
    - append-only storage;
    - immutable logs;
    - retention policy;
    - search/analytics;
    - access control.
    """

    def __init__(self, path: str):
        self.path = path

    def log(self, decision: Decision) -> None:
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "a", encoding="utf-8") as file:
            file.write(json.dumps(decision.as_dict(), ensure_ascii=False) + "\n")
