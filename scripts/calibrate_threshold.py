"""Calibrate OOD threshold on a dedicated development query set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge.embedder import DEFAULT_MODEL, SentenceTransformerEmbedder  # noqa: E402
from knowledge.vector_store import DEFAULT_DB_PATH, VectorStore, collection_name  # noqa: E402


def select_threshold(in_scores: list[float], ood_scores: list[float]) -> tuple[float, float]:
    if not in_scores or not ood_scores:
        raise ValueError("Data kalibrasi harus memiliki kueri in-domain dan out-of-domain.")

    scores = sorted(set(in_scores + ood_scores))
    candidates = [scores[0] - 1e-6]
    candidates.extend((left + right) / 2 for left, right in zip(scores, scores[1:]))
    candidates.append(scores[-1] + 1e-6)

    def balanced_accuracy(threshold: float) -> float:
        accepted = sum(score >= threshold for score in in_scores) / len(in_scores)
        rejected = sum(score < threshold for score in ood_scores) / len(ood_scores)
        return (accepted + rejected) / 2

    threshold = max(candidates, key=lambda value: (balanced_accuracy(value), value))
    return threshold, balanced_accuracy(threshold)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--chunk-words", type=int, default=180)
    parser.add_argument("--overlap", type=int, default=36)
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--queries", default=str(ROOT / "data" / "ood_calibration_queries.json"))
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    name = collection_name(args.model, args.chunk_words, args.overlap)
    store = VectorStore(SentenceTransformerEmbedder(args.model), name, args.db_path)
    if store.count() == 0:
        parser.error(f"Koleksi '{name}' kosong. Jalankan scripts/build_index.py dengan konfigurasi yang sama.")

    queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))["queries"]
    in_scores: list[float] = []
    ood_scores: list[float] = []
    details = []
    for query in queries:
        hits = store.search(query["query"], k=1)
        score = hits[0].similarity if hits else 0.0
        is_ood = query["type"] == "out_of_domain"
        (ood_scores if is_ood else in_scores).append(score)
        details.append({"id": query["id"], "type": query["type"], "top1_score": round(score, 6)})

    threshold, balanced_accuracy = select_threshold(in_scores, ood_scores)
    result = {
        "model": args.model,
        "collection": name,
        "development_query_file": str(Path(args.queries).relative_to(ROOT)),
        "in_domain_count": len(in_scores),
        "out_of_domain_count": len(ood_scores),
        "threshold": round(threshold, 6),
        "balanced_accuracy_dev": round(balanced_accuracy, 6),
        "in_domain_accepted_dev": sum(score >= threshold for score in in_scores),
        "out_of_domain_rejected_dev": sum(score < threshold for score in ood_scores),
        "scores": details,
        "warning": "Ambang dipilih pada data dev; metrik dev bukan estimasi performa holdout.",
    }
    output = Path(args.output) if args.output else ROOT / "reports" / f"calibration_{name}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
