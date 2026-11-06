"""Jalankan build_index + run_benchmark untuk 4 konfigurasi, lalu buat tabel ringkasan.

    uv run python scripts/run_all.py

Keluaran: reports/benchmark_<koleksi>.md|csv per konfigurasi dan reports/summary_ablation.md
(tabel siap salin ke Bagian 6.4 laporan).
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge.vector_store import collection_name  # noqa: E402

E5 = "intfloat/multilingual-e5-small"
MINILM = "paraphrase-multilingual-MiniLM-L12-v2"
CONFIGS = [(E5, 180, 36), (E5, 120, 24), (MINILM, 80, 16), (MINILM, 120, 24)]


def run(script: str, model: str, cw: int, ov: int, extra: list[str] | None = None) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / script), "--model", model,
           "--chunk-words", str(cw), "--overlap", str(ov), *(extra or [])]
    print("\n>>>", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(model: str, cw: int, ov: int) -> str:
    name = collection_name(model, cw, ov)
    rows = list(csv.DictReader((ROOT / "reports" / f"benchmark_{name}.csv").open(encoding="utf-8")))
    syn = [r for r in rows if r["type"] == "synonym"]
    amb = [r for r in rows if r["type"] == "ambiguous"]
    inn = [r for r in rows if r["type"] != "out_of_domain"]
    ood = [r for r in rows if r["type"] == "out_of_domain"]
    md = (ROOT / "reports" / f"benchmark_{name}.md").read_text(encoding="utf-8")
    m = re.search(r"Ambang OOD.*?: ([\d.]+)\*\* — in-domain diterima (\d+)/(\d+), out-of-domain ditolak (\d+)/(\d+)", md)
    thr, a, b, c, d = m.groups() if m else ("?", "?", "?", "?", "?")
    n_chunks = re.search(r"· (\d+) chunk", md)
    f = lambda xs, k: mean([float(r[k]) for r in xs])  # noqa: E731
    return (f"| {model.split('/')[-1]} · {cw}/{ov} | {n_chunks.group(1) if n_chunks else '?'} | "
            f"{f(syn, 'hit@1'):.2f} | {f(syn, 'hit@3'):.2f} | {f(syn, 'rr'):.2f} | {f(amb, 'hit@3'):.2f} | "
            f"{mean([float(r['top1_score']) for r in inn]):.3f} | {mean([float(r['top1_score']) for r in ood]):.3f} | "
            f"{thr} | {a}/{b} | {c}/{d} |")


def main() -> None:
    for model, cw, ov in CONFIGS:
        run("build_index.py", model, cw, ov, ["--reset"])
        run("run_benchmark.py", model, cw, ov)

    header = ("| Konfigurasi | Chunk | Hit@1 sin. | Hit@3 sin. | MRR sin. | Hit@3 ambigu | Skor top-1 in-domain "
              "| Skor top-1 OOD | Ambang OOD | In-domain diterima | OOD ditolak |\n|---|---|---|---|---|---|---|---|---|---|---|")
    table = "\n".join([header, *(summarize(*c) for c in CONFIGS)])
    out = ROOT / "reports" / "summary_ablation.md"
    out.write_text("# Ringkasan ablation\n\n" + table + "\n", encoding="utf-8")
    print("\n" + table + f"\n\nTersimpan: {out}")


if __name__ == "__main__":
    main()