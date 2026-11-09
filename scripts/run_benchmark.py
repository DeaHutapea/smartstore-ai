"""Benchmark temu balik semantik + kalibrasi ambang out-of-domain.

    uv run python scripts/run_benchmark.py                      # model default, indeks harus sudah dibangun
    uv run python scripts/run_benchmark.py --model paraphrase-multilingual-MiniLM-L12-v2 --chunk-words 120 --overlap 24

Keluaran: reports/benchmark_<koleksi>.csv & .md (siap ditempel ke laporan).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge.embedder import DEFAULT_MODEL, SentenceTransformerEmbedder  # noqa: E402
from knowledge.retriever import DEFAULT_THRESHOLD  # noqa: E402
from knowledge.vector_store import DEFAULT_DB_PATH, VectorStore, collection_name  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--chunk-words", type=int, default=180)
    ap.add_argument("--overlap", type=int, default=36)
    ap.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    ap.add_argument("--queries", default=str(ROOT / "data" / "benchmark_queries.json"))
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Ambang yang sudah dikalibrasi pada data dev terpisah; tidak dikalibrasi dari kueri benchmark ini.",
    )
    a = ap.parse_args()

    if not 0.0 <= a.threshold <= 1.0:
        ap.error("--threshold harus berada pada rentang 0.0 sampai 1.0")

    name = collection_name(a.model, a.chunk_words, a.overlap)
    store = VectorStore(SentenceTransformerEmbedder(a.model), name, a.db_path)
    if store.count() == 0:
        sys.exit(f"Koleksi '{name}' kosong. Jalankan scripts/build_index.py dengan opsi yang sama.")

    queries = json.loads(Path(a.queries).read_text(encoding="utf-8"))["queries"]
    rows = []
    for q in queries:
        hits = store.search(q["query"], k=store.count())
        docs_ranked: list[tuple[str, float]] = []
        seen_docs: set[str] = set()
        for hit in hits:
            doc_id = hit.metadata["doc_id"]
            if doc_id not in seen_docs:
                docs_ranked.append((doc_id, hit.similarity))
                seen_docs.add(doc_id)
                if len(docs_ranked) == a.k:
                    break
        exp = set(q["expected_docs"])
        rank = next((i + 1 for i, (doc_id, _) in enumerate(docs_ranked) if doc_id in exp), None)
        top_score = hits[0].similarity if hits else 0.0
        top_doc = docs_ranked[0][0] if docs_ranked else ""
        rows.append({
            "id": q["id"], "type": q["type"], "query": q["query"],
            "top1_doc": top_doc, "top1_section": hits[0].metadata.get("section", "") if hits else "",
            "top1_score": round(top_score, 4),
            "top2_score": round(docs_ranked[1][1], 4) if len(docs_ranked) > 1 else "",
            "expected": ",".join(sorted(exp)), "rank_of_expected": rank or "",
            "hit@1": int(rank == 1) if exp else "", "hit@3": int(bool(rank and rank <= 3)) if exp else "",
            "rr": round(1 / rank, 4) if rank else (0 if exp else ""),
            "retrieved_doc_ids": ";".join(doc_id for doc_id, _ in docs_ranked),
            "cosine_scores": ";".join(f"{score:.4f}" for _, score in docs_ranked),
            "is_rejected": top_score < a.threshold,
        })

    in_rows = [r for r in rows if r["type"] != "out_of_domain"]
    ood_rows = [r for r in rows if r["type"] == "out_of_domain"]

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    lines = [
        f"# Benchmark `{name}`",
        "",
        f"Model: `{a.model}` · chunk={a.chunk_words} kata · overlap={a.overlap} · {store.count()} chunk",
        f"Ambang OOD dari kalibrasi data dev terpisah: **{a.threshold:.3f}**.",
        "",
    ]
    lines += ["| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |", "|---|---|---|---|---|---|"]
    for t in ("synonym", "ambiguous"):
        sub = [r for r in rows if r["type"] == t]
        lines.append(f"| {t} | {len(sub)} | {mean([r['hit@1'] for r in sub]):.2f} | {mean([r['hit@3'] for r in sub]):.2f} | "
                     f"{mean([r['rr'] for r in sub]):.2f} | {mean([r['top1_score'] for r in sub]):.3f} |")
    lines.append(f"| out_of_domain | {len(ood_rows)} | – | – | – | {mean([r['top1_score'] for r in ood_rows]):.3f} |")
    tp = sum(r["top1_score"] >= a.threshold for r in in_rows)
    tn = sum(r["top1_score"] < a.threshold for r in ood_rows)
    ood_tp = sum(r["top1_score"] < a.threshold for r in ood_rows)
    ood_fp = sum(r["top1_score"] < a.threshold for r in in_rows)
    ood_fn = len(ood_rows) - ood_tp
    ood_precision = ood_tp / (ood_tp + ood_fp) if ood_tp + ood_fp else 0.0
    ood_recall = ood_tp / (ood_tp + ood_fn) if ood_tp + ood_fn else 0.0
    ood_f1 = (
        2 * ood_precision * ood_recall / (ood_precision + ood_recall)
        if ood_precision + ood_recall
        else 0.0
    )
    lines += ["", f"**Hasil holdout dengan ambang dev** — in-domain diterima {tp}/{len(in_rows)}, "
              f"out-of-domain ditolak {tn}/{len(ood_rows)}.",
              f"Precision penolakan OOD={ood_precision:.3f}, recall={ood_recall:.3f}, F1={ood_f1:.3f}.",
              "", "| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['type']} | {r['query']} | {r['top1_doc']} | {r['top1_score']} | {r['expected'] or '–'} | {r['rank_of_expected'] or '–'} |")
    lines += [
        "",
        "Catatan: angka OOD dihitung pada set evaluasi holdout. Ukuran set kecil, jadi hasil ini belum membuktikan generalisasi ke kueri produksi.",
    ]

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    with (out / f"benchmark_{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out / f"benchmark_{name}.md").write_text("\n".join(lines), encoding="utf-8")
    with (out / f"predictions_{name}.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["query_id", "retrieved_doc_ids", "cosine_scores", "is_rejected"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "query_id": row["id"],
                "retrieved_doc_ids": row["retrieved_doc_ids"],
                "cosine_scores": row["cosine_scores"],
                "is_rejected": row["is_rejected"],
            })
    print("\n".join(lines))


if __name__ == "__main__":
    main()
