"""
Pipeline API Utama RAG SmartStore AI (6 Fungsi Utama)
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path

from .loader import Document, load_documents_from_dir
from .chunker import chunk_documents as _chunk_docs
from .vector_store import SmartStoreVectorStore
from .config import DEFAULT_CHROMA_DIR, DEFAULT_SIMILARITY_THRESHOLD


def load_documents(corpus_dir: str = "./data/raw") -> List[Document]:
    """1. Memuat seluruh dokumen dari folder korpus."""
    return load_documents_from_dir(corpus_dir)


def chunk_documents(
    documents: List[Document],
    preset: str = "medium",
    custom_size: int = None,
    custom_overlap: int = None
) -> List[Document]:
    """2. Memotong dokumen secara word-aware dengan overlap."""
    return _chunk_docs(documents, preset=preset, custom_size=custom_size, custom_overlap=custom_overlap)


def create_embeddings(model_name: str = None) -> SmartStoreVectorStore:
    """3. Inisialisasi model embeddings & vector store."""
    if model_name:
        return SmartStoreVectorStore(model_name=model_name)
    return SmartStoreVectorStore()


def ingest_documents(
    corpus_dir: str = "./data/raw",
    db_dir: str = DEFAULT_CHROMA_DIR,
    chunk_preset: str = "medium",
    reset_db: bool = True
) -> SmartStoreVectorStore:
    """4. Menjalankan pipeline ingestion ujung-ke-ujung (Load -> Chunk -> Embed -> Persist)."""
    docs = load_documents(corpus_dir)
    if not docs:
        print(f"[WARNING] Tidak ada dokumen di '{corpus_dir}'")
        return None

    chunks = chunk_documents(docs, preset=chunk_preset)
    store = SmartStoreVectorStore(db_dir=db_dir)
    if reset_db:
        store.reset_database()
    store.add_documents(chunks)
    print(f"[SUCCESS] Berhasil mengindeks {len(chunks)} chunk dari {len(docs)} halaman dokumen.")
    return store


def retrieve_documents(
    query: str,
    top_k: int = 3,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    filter_dict: Optional[Dict[str, Any]] = None,
    db_dir: str = DEFAULT_CHROMA_DIR
) -> Dict[str, Any]:
    """5. Mengambil dokumen terdekat berdasarkan Top-K Cosine Similarity."""
    store = SmartStoreVectorStore(db_dir=db_dir)
    raw_results = store.similarity_search(query, top_k=top_k, filter_dict=filter_dict)

    if not raw_results or raw_results[0]["score"] < threshold:
        top_score = raw_results[0]["score"] if raw_results else 0.0
        return {
            "status": "REJECTED_OUT_OF_DOMAIN",
            "query": query,
            "top_score": top_score,
            "threshold": threshold,
            "message": f"Kueri di luar cakupan domain bisnis. (Score {top_score} < Threshold {threshold})",
            "documents": []
        }

    return {
        "status": "SUCCESS",
        "query": query,
        "top_score": raw_results[0]["score"],
        "threshold": threshold,
        "documents": raw_results
    }


def query_knowledge_base(
    query: str,
    top_k: int = 3,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> Dict[str, Any]:
    """6. API ringkas untuk query basis pengetahuan."""
    return retrieve_documents(query=query, top_k=top_k, threshold=threshold)