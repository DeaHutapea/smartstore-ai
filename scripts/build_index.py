"""Bangun indeks ChromaDB dari korpus. Contoh:

    uv run python scripts/build_index.py --reset
    uv run python scripts/build_index.py --model paraphrase-multilingual-MiniLM-L12-v2 --chunk-words 120 --overlap 24 --reset
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge.chunker import chunk_text  # noqa: E402
from knowledge.corpus_loader import DEFAULT_CORPUS_DIR, DEFAULT_MANIFEST, load_corpus  # noqa: E402
from knowledge.embedder import DEFAULT_MODEL, SentenceTransformerEmbedder  # noqa: E402
from knowledge.vector_store import DEFAULT_DB_PATH, VectorStore, collection_name  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    ap.add_argument("--corpus-dir", default=str(DEFAULT_CORPUS_DIR))
    ap.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--chunk-words", type=int, default=180)
    ap.add_argument("--overlap", type=int, default=36)
    ap.add_argument("--ocr", action="store_true", help="coba OCR untuk PDF scan (butuh pytesseract)")
    ap.add_argument("--reset", action="store_true", help="hapus koleksi lama dengan konfigurasi sama")
    ap.add_argument(
        "--allow-partial-corpus",
        action="store_true",
        help="izinkan indeks parsial jika sumber manifest belum tersedia",
    )
    a = ap.parse_args()

    docs, report = load_corpus(a.manifest, a.corpus_dir, use_ocr=a.ocr)
    for w in report.warnings:
        print("[WARN]", w)
    for doc_id, why in report.skipped:
        print(f"[SKIP] {doc_id}: {why}")
    missing_sources = [(doc_id, why) for doc_id, why in report.skipped if why == "file tidak ditemukan"]
    if missing_sources and not a.allow_partial_corpus:
        missing_ids = ", ".join(doc_id for doc_id, _ in missing_sources)
        sys.exit(
            f"Korpus tidak lengkap; file untuk {missing_ids} tidak ditemukan. "
            "Sediakan sumber lokal sesuai docs/corpus_sources.md atau gunakan --allow-partial-corpus."
        )

    out_dir = ROOT / "data" / "processed"
    out_dir.mkdir(exist_ok=True)

    embedder = SentenceTransformerEmbedder(a.model)
    name = collection_name(a.model, a.chunk_words, a.overlap)
    store = VectorStore(embedder, name, a.db_path, reset=a.reset)

    stats = []
    for doc in docs:
        (out_dir / f"{doc.doc_id}.txt").write_text(doc.text, encoding="utf-8")  # bukti pembersihan
        chunks = chunk_text(doc.text, a.chunk_words, a.overlap)
        store.add_document(doc, chunks, a.chunk_words, a.overlap)
        wc = [c.word_count for c in chunks]
        stats.append({"doc_id": doc.doc_id, "words": len(doc.text.split()), "chunks": len(chunks),
                      "min_words": min(wc), "max_words": max(wc), "mean_words": round(sum(wc) / len(wc), 1)})
        print(f"[OK] {doc.doc_id}: {len(chunks)} chunk")

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / f"index_stats_{name}.json").write_text(
        json.dumps({"collection": name, "model": a.model, "total_chunks": store.count(), "docs": stats,
                    "skipped": report.skipped}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKoleksi '{name}': {store.count()} chunk tersimpan di {a.db_path}")


if __name__ == "__main__":
    main()
