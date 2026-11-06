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
from knowledge.vector_store import DEFAULT_DB_PATH, VectorStore, collection_name  # noqa: E402


def best_threshold(in_scores: list[float], ood_scores: list[float]) -> tuple[float, float]:
    """Cari ambang yang memaksimalkan balanced accuracy (in-domain diterima, OOD ditolak)."""
    cands = sorted(set(in_scores + ood_scores))
    best_t, best_acc = 0.0, -1.0
    for lo, hi in zip(cands, cands[1:] + [cands[-1] + 0.01]):
        t = (lo + hi) / 2
        tpr = sum(s >= t for s in in_scores) / len(in_scores)
        tnr = sum(s < t for s in ood_scores) / len(ood_scores)
        if (tpr + tnr) / 2 > best_acc:
            best_t, best_acc = t, (tpr + tnr) / 2
    return best_t, best_acc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--chunk-words", type=int, default=180)
    ap.add_argument("--overlap", type=int, default=36)
    ap.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    ap.add_argument("--queries", default=str(ROOT / "data" / "benchmark_queries.json"))
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()

    name = collection_name(a.model, a.chunk_words, a.overlap)
    store = VectorStore(SentenceTransformerEmbedder(a.model), name, a.db_path)
    if store.count() == 0:
        sys.exit(f"Koleksi '{name}' kosong. Jalankan scripts/build_index.py dengan opsi yang sama.")

    queries = json.loads(Path(a.queries).read_text(encoding="utf-8"))["queries"]
    rows = []
    for q in queries:
        hits = store.search(q["query"], k=a.k * 3)
        docs_ranked: list[str] = []
        for h in hits:  # peringkat level-dokumen (chunk terbaik per dokumen)
            if h.metadata["doc_id"] not in docs_ranked:
                docs_ranked.append(h.metadata["doc_id"])
        exp = set(q["expected_docs"])
        rank = next((i + 1 for i, d in enumerate(docs_ranked) if d in exp), None)
        rows.append({
            "id": q["id"], "type": q["type"], "query": q["query"],
            "top1_doc": hits[0].metadata["doc_id"], "top1_section": hits[0].metadata.get("section", ""),
            "top1_score": round(hits[0].similarity, 4),
            "top2_score": round(hits[1].similarity, 4) if len(hits) > 1 else "",
            "expected": ",".join(sorted(exp)), "rank_of_expected": rank or "",
            "hit@1": int(rank == 1) if exp else "", "hit@3": int(bool(rank and rank <= 3)) if exp else "",
            "rr": round(1 / rank, 4) if rank else (0 if exp else ""),
        })

    in_rows = [r for r in rows if r["type"] != "out_of_domain"]
    ood_rows = [r for r in rows if r["type"] == "out_of_domain"]
    thr, bacc = best_threshold([r["top1_score"] for r in in_rows], [r["top1_score"] for r in ood_rows])

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    lines = [f"# Benchmark `{name}`", "", f"Model: `{a.model}` · chunk={a.chunk_words} kata · overlap={a.overlap} · {store.count()} chunk", ""]
    lines += ["| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |", "|---|---|---|---|---|---|"]
    for t in ("synonym", "ambiguous"):
        sub = [r for r in rows if r["type"] == t]
        lines.append(f"| {t} | {len(sub)} | {mean([r['hit@1'] for r in sub]):.2f} | {mean([r['hit@3'] for r in sub]):.2f} | "
                     f"{mean([r['rr'] for r in sub]):.2f} | {mean([r['top1_score'] for r in sub]):.3f} |")
    lines.append(f"| out_of_domain | {len(ood_rows)} | – | – | – | {mean([r['top1_score'] for r in ood_rows]):.3f} |")
    tp = sum(r["top1_score"] >= thr for r in in_rows); tn = sum(r["top1_score"] < thr for r in ood_rows)
    lines += ["", f"**Ambang OOD (kalibrasi, balanced accuracy={bacc:.2f}): {thr:.3f}** — "
              f"in-domain diterima {tp}/{len(in_rows)}, out-of-domain ditolak {tn}/{len(ood_rows)}.",
              "", "| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['type']} | {r['query']} | {r['top1_doc']} | {r['top1_score']} | {r['expected'] or '–'} | {r['rank_of_expected'] or '–'} |")

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    with (out / f"benchmark_{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out / f"benchmark_{name}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
