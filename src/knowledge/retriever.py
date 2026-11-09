"""Retriever: top-k semantik + penolakan kueri out-of-domain berbasis ambang cosine."""

from __future__ import annotations

from dataclasses import dataclass

from .embedder import DEFAULT_MODEL
from .vector_store import Hit, VectorStore, collection_name

DEFAULT_THRESHOLD = 0.850363


@dataclass
class RetrievalResult:
    query: str
    hits: list[Hit]
    top_score: float
    in_domain: bool  # False -> sebaiknya ditolak ("di luar cakupan basis pengetahuan")


class Retriever:
    def __init__(self, store: VectorStore, threshold: float | None = None):
        if threshold is None:
            default_collection = collection_name(DEFAULT_MODEL, 180, 36)
            if store.embedder.model_name != DEFAULT_MODEL or store.collection.name != default_collection:
                raise ValueError(
                    "Ambang default dikalibrasi untuk E5 dengan konfigurasi chunk 180/36; "
                    "berikan threshold terkalibrasi untuk konfigurasi lain."
                )
            threshold = DEFAULT_THRESHOLD
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold harus berada pada rentang 0.0 sampai 1.0")
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
