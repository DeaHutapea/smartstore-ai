"""Retriever: top-k semantik + penolakan kueri out-of-domain berbasis ambang cosine."""

from __future__ import annotations

from dataclasses import dataclass

from .vector_store import Hit, VectorStore


@dataclass
class RetrievalResult:
    query: str
    hits: list[Hit]
    top_score: float
    in_domain: bool  # False -> sebaiknya ditolak ("di luar cakupan basis pengetahuan")


class Retriever:
    def __init__(self, store: VectorStore, threshold: float = 0.80):
        self.store = store
        self.threshold = threshold

    def retrieve(self, query: str, k: int = 5, where: dict | None = None, dedupe_docs: bool = False) -> RetrievalResult:
        hits = self.store.search(query, k=k * 3 if dedupe_docs else k, where=where)
        if dedupe_docs:
            seen, uniq = set(), []
            for h in hits:
                if h.metadata["doc_id"] not in seen:
                    seen.add(h.metadata["doc_id"])
                    uniq.append(h)
            hits = uniq[:k]
        top = hits[0].similarity if hits else 0.0
        return RetrievalResult(query, hits, top, top >= self.threshold)
