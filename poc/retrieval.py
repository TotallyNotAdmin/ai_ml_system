import math
import re
from collections import Counter
from typing import List, Optional

from .models import RetrievedDoc

TOKEN_RE = re.compile(r"[а-яёa-z0-9]+")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


class SimpleRetriever:
    """
    Упрощённый локальный retrieval для poc.

    В целевой системе:
    - embeddings;
    - vector DB;
    - hybrid BM25 + dense retrieval;
    - reranker;
    - incident-aware deduplication.
    """

    def __init__(self, docs):
        self.docs = docs
        self.doc_vectors = []
        self.df = Counter()

        for doc in docs:
            text = " ".join(
                [
                    doc.get("title", ""),
                    doc.get("text", ""),
                    " ".join(doc.get("tags", [])),
                    doc.get("topic", ""),
                ]
            )
            vector = Counter(tokenize(text))
            self.doc_vectors.append(vector)

            for term in vector:
                self.df[term] += 1

        self.n_docs = len(docs)

    def _weight(self, vector: Counter) -> dict:
        weighted = {}

        for term, count in vector.items():
            idf = math.log((1 + self.n_docs) / (1 + self.df.get(term, 0))) + 1.0
            weighted[term] = (1.0 + math.log(count)) * idf

        return weighted

    def search(
        self,
        query: str,
        topic: Optional[str] = None,
        top_k: int = 3,
    ) -> List[RetrievedDoc]:
        raw_query = query if not topic else f"{query} {topic}"
        query_vector = self._weight(Counter(tokenize(raw_query)))
        query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1.0

        results = []

        for index, doc in enumerate(self.docs):
            doc_vector = self._weight(self.doc_vectors[index])
            doc_norm = math.sqrt(sum(value * value for value in doc_vector.values())) or 1.0

            dot = sum(weight * doc_vector.get(term, 0.0) for term, weight in query_vector.items())
            score = dot / (query_norm * doc_norm)

            if topic and doc.get("topic") == topic:
                score = min(1.0, score * 1.15 + 0.05)

            if score > 0:
                results.append(
                    RetrievedDoc(
                        id=doc["id"],
                        title=doc.get("title", ""),
                        text=doc.get("text", ""),
                        score=score,
                        topic=doc.get("topic", ""),
                        auto_allowed=bool(doc.get("auto_allowed", False)),
                    )
                )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]
