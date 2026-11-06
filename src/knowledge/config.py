"""
Konfigurasi & Preset Chunking RAG SmartStore AI (T03)
"""

from dataclasses import dataclass
from typing import Dict, Tuple

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "smartstore_knowledge_base"
DEFAULT_SIMILARITY_THRESHOLD = 0.50  # Cosine Similarity minimum


@dataclass
class ChunkConfig:
    chunk_size: int
    chunk_overlap: int


# Preset ukuran chunk (diukur dalam estimasi karakter, 1 token ≈ 4 karakter)
CHUNK_PRESETS: Dict[str, ChunkConfig] = {
    "small": ChunkConfig(chunk_size=400, chunk_overlap=80),     # ~100 tokens
    "medium": ChunkConfig(chunk_size=1000, chunk_overlap=200),  # ~250 tokens
    "large": ChunkConfig(chunk_size=2000, chunk_overlap=400),   # ~500 tokens
}


def get_chunk_config(preset: str = "medium", custom_size: int = None, custom_overlap: int = None) -> ChunkConfig:
    if custom_size is not None and custom_overlap is not None:
        return ChunkConfig(chunk_size=custom_size, chunk_overlap=custom_overlap)
    return CHUNK_PRESETS.get(preset.lower(), CHUNK_PRESETS["medium"])