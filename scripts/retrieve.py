"""
Script CLI untuk Pengujian Temu Balik Semantik (Semantic Retrieval)
Lokasi: scripts/retrieve.py
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledge.pipeline import retrieve_documents


def main():
    parser = argparse.ArgumentParser(description="Pencarian semantik pada basis pengetahuan SmartStore AI.")
    parser.add_argument("--query", type=str, help="Teks kueri pencarian")
    parser.add_argument("--top-k", type=int, default=3, help="Jumlah hasil teratas")
    parser.add_argument("--threshold", type=float, default=0.50, help="Ambang batas Similarity Guardrail (0.0 - 1.0)")
    parser.add_argument("--db-dir", type=str, default="./chroma_db", help="Folder penyimpanan ChromaDB")

    args = parser.parse_args()

    if args.query:
        run_query(args.query, args.top_k, args.threshold, args.db_dir)
        return

    print("=== [STEP 3] Semantic Search Engine CLI (Tekan Ctrl+C untuk keluar) ===")
    while True:
        try:
            query_text = input("\nMasukkan Kueri Uji Bisnis: ").strip()
            if not query_text:
                continue
            run_query(query_text, args.top_k, args.threshold, args.db_dir)
        except (KeyboardInterrupt, EOFError):
            print("\nPengujian selesai.")
            break


def run_query(query: str, top_k: int, threshold: float, db_dir: str):
    print(f"\n🔍 Mencari: '{query}' (Top-K: {top_k}, Threshold: {threshold})")
    res = retrieve_documents(query=query, top_k=top_k, threshold=threshold, db_dir=db_dir)

    print(f"Status Retrieval : {res['status']}")
    print(f"Skor Teratas     : {res.get('top_score', 0.0)}")

    if res["status"] == "REJECTED_OUT_OF_DOMAIN":
        print(f"❌ [GUARDRAIL ACTION] {res['message']}")
        return

    print("\n--- Dokumen Relevan Ditemukan ---")
    for idx, doc in enumerate(res["documents"], start=1):
        meta = doc["metadata"]
        print(f"[{idx}] Similarity Score: {doc['score']} | File: {meta.get('document_name')} (Page {meta.get('page_number')})")
        print(f"    Platform: {meta.get('platform')} | Category: {meta.get('category')} | Chunk ID: {meta.get('chunk_id')}")
        print(f"    Isi Teks : {doc['content'][:150]}...\n")


if __name__ == "__main__":
    main()