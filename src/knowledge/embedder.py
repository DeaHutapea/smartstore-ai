"""Wrapper Sentence-Transformers (lazy import, normalisasi L2 -> cosine = dot product)."""

from __future__ import annotations

import re
from typing import Protocol, Sequence

DEFAULT_MODEL = "intfloat/multilingual-e5-small"
ALT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class Embedder(Protocol):
    model_name: str

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


def model_slug(model_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", model_name.split("/")[-1]).strip("_").lower()[:40]


class SentenceTransformerEmbedder:
    """Model E5 butuh prefix 'query: ' / 'passage: '; model lain tidak."""

    def __init__(self, model_name: str = DEFAULT_MODEL, batch_size: int = 32) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.batch_size = batch_size
        self._model = SentenceTransformer(model_name)
        self._is_e5 = "e5" in model_name.lower()

    def _encode(self, texts: Sequence[str]) -> list[list[float]]:
        vecs = self._model.encode(
            list(texts), batch_size=self.batch_size, normalize_embeddings=True, show_progress_bar=len(texts) > 64
        )
        return vecs.tolist()

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return self._encode([f"passage: {t}" for t in texts] if self._is_e5 else texts)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([f"query: {text}" if self._is_e5 else text])[0]
