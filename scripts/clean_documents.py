"""
Script CLI untuk Pembacaan & Pembersihan Dokumen Korpus (PDF, MD, TXT)
Lokasi: scripts/clean_documents.py
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledge.loader import load_documents_from_dir


def main():
    corpus_dir = Path("./data/raw")
    print("=== [STEP 1] Inspeksi & Cleaning Dokumen Korpus ===")
    print(f"Memindai direktori: {corpus_dir.resolve()}\n")

    if not corpus_dir.exists():
        print(f"[ERROR] Folder '{corpus_dir}' tidak ditemukan. Buat folder dan letakkan dokumen korpus.")
        sys.exit(1)

    docs = load_documents_from_dir(corpus_dir)

    if not docs:
        print("[WARNING] Tidak ada dokumen .pdf, .md, atau .txt ditemukan.")
        return

    print(f"✓ Total Segmen/Halaman Dokumen Dimuat: {len(docs)}\n")
    print("--- Sample Metadata Dokumen ---")
    for idx, doc in enumerate(docs[:5], start=1):
        meta = doc.metadata
        print(f"[{idx}] {meta.get('document_name')} | Platform: {meta.get('platform')} | Category: {meta.get('category')} | Page: {meta.get('page_number')}")
        print(f"    Pratinjau Teks: {doc.page_content[:100]}...\n")


if __name__ == "__main__":
    main()