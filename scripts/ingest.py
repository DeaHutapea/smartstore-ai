"""
Script CLI Ingestion Pipeline Korpus ke Vector Store ChromaDB
Lokasi: scripts/ingest.py
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledge.pipeline import ingest_documents


def main():
    parser = argparse.ArgumentParser(description="Ingest dokumen korpus SmartStore AI ke ChromaDB.")
    parser.add_argument("--corpus-dir", type=str, default="./data/raw", help="Folder sumber korpus")
    parser.add_argument("--db-dir", type=str, default="./chroma_db", help="Folder penyimpanan ChromaDB")
    parser.add_argument("--preset", type=str, default="medium", choices=["small", "medium", "large"], help="Preset chunking")
    parser.add_argument("--no-reset", action="store_true", help="Jangan hapus database lama saat ingestion")

    args = parser.parse_args()

    print("=== [STEP 2] Memulai Pipeline Ingestion RAG ===")
    print(f"• Corpus Directory : {args.corpus_dir}")
    print(f"• Vector Database  : {args.db_dir}")
    print(f"• Chunking Preset  : {args.preset}")
    print(f"• Reset Database   : {not args.no_reset}\n")

    store = ingest_documents(
        corpus_dir=args.corpus_dir,
        db_dir=args.db_dir,
        chunk_preset=args.preset,
        reset_db=not args.no_reset
    )

    if store:
        print("\n✓ [SUCCESS] Ingestion selesai secara persisten di folder './chroma_db'.")


if __name__ == "__main__":
    main()