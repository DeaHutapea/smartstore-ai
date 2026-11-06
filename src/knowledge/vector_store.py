"""
Manajemen Vector Store ChromaDB Persisten & Embeddings
"""

from __future__ import annotations
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .loader import Document
from .config import EMBEDDING_MODEL_NAME, DEFAULT_CHROMA_DIR, COLLECTION_NAME


class SmartStoreVectorStore:
    def __init__(
        self,
        db_dir: str = DEFAULT_CHROMA_DIR,
        collection_name: str = COLLECTION_NAME,
        model_name: str = EMBEDDING_MODEL_NAME
    ):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.model_name = model_name
        
        # Inisialisasi model Sentence-Transformers
        self.embedding_model = SentenceTransformer(self.model_name)
        
        # Inisialisasi Chroma Persistent Client
        self.client = chromadb.PersistentClient(path=self.db_dir)
        
        # Memastikan Koleksi Menggunakan Eksplisit Cosine Distance
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # EKSPLISIT COSINE DISTANCE
        )

    def reset_database(self):
        """Menghapus koleksi lama dan membuat ulang direktori database."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Document]):
        """Mengonversi potongan dokumen menjadi embedding dan menyimpannya ke ChromaDB."""
        if not documents:
            return

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [doc.metadata["chunk_id"] for doc in documents]

        # Ekstraksi Dense Embeddings
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True).tolist()

        # Batch Insertion
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def similarity_search(
        self,
        query: str,
        top_k: int = 3,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Melakukan pencarian kemiripan semantik.
        Mengubah Cosine Distance menjadi Cosine Similarity Score (Score = 1 - Distance).
        """
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).tolist()

        kwargs = {
            "query_embeddings": query_embedding,
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if filter_dict:
            kwargs["where"] = filter_dict

        results = self.collection.query(**kwargs)

        search_results = []
        if results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc_text, meta, dist in zip(docs, metas, distances):
                # Cosine Similarity = 1 - Cosine Distance
                similarity_score = round(1.0 - float(dist), 4)
                search_results.append({
                    "score": similarity_score,
                    "distance": round(float(dist), 4),
                    "content": doc_text,
                    "metadata": meta
                })

        return search_results