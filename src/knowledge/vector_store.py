"""ChromaDB persisten (cosine) + metadata lengkap untuk filter/hybrid search."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chunker import Chunk
from .corpus_loader import Document
from .embedder import Embedder, model_slug

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "chroma_db"


@dataclass
class Hit:
    chunk_id: str
    text: str
    similarity: float  # cosine similarity = 1 - cosine distance
    metadata: dict


def collection_name(model_name: str, chunk_words: int, overlap_words: int) -> str:
    # satu koleksi per konfigurasi -> perbandingan model/chunk tidak saling menimpa
    return f"kb_{model_slug(model_name)}_c{chunk_words}_o{overlap_words}"[:63]


class VectorStore:
    def __init__(self, embedder: Embedder, name: str, db_path: str | Path = DEFAULT_DB_PATH, reset: bool = False):
        import chromadb

        self.embedder = embedder
        self.client = chromadb.PersistentClient(path=str(db_path))
        if reset:
            try:
                self.client.delete_collection(name)
            except Exception:  # koleksi belum ada
                pass
        self.collection = self.client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

    def count(self) -> int:
        return self.collection.count()

    def add_document(self, doc: Document, chunks: list[Chunk], chunk_words: int, overlap_words: int) -> int:
        if not chunks:
            return 0
        ids = [f"{doc.doc_id}::{c.index:04d}" for c in chunks]
        metas = []
        for c in chunks:
            meta = {k: ("" if v is None else v) for k, v in doc.meta.items()}
            meta.update(
                chunk_index=c.index,
                n_chunks=len(chunks),
                word_count=c.word_count,
                section=c.section,
                chunk_words_cfg=chunk_words,
                overlap_words_cfg=overlap_words,
                embedding_model=self.embedder.model_name,
            )
            metas.append(meta)
        texts = [c.text for c in chunks]
        self.collection.upsert(
            ids=ids, documents=texts, metadatas=metas, embeddings=self.embedder.embed_passages(texts)
        )
        return len(chunks)

    def search(self, query: str, k: int = 5, where: dict | None = None) -> list[Hit]:
        res = self.collection.query(
            query_embeddings=[self.embedder.embed_query(query)],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return [
            Hit(i, d, 1.0 - dist, m)
            for i, d, m, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]
