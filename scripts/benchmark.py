#!/usr/bin/env python3
"""
SmartStore AI T03 - Benchmark & Evaluation Script
=================================================
Menghitung metrik evaluasi Retrieval-Augmented Generation (RAG):
1. Precision@K
2. Recall@K
3. Mean Reciprocal Rank (MRR)
4. OOD Rejection Precision (serta OOD Rejection Recall/F1)
5. Analisis Distribusi Cosine Similarity & Visualisasi

Catatan Penting:
- Script ini TIDAK mengubah source code T01 maupun T02.
- Script ini membaca file hasil prediksi dari pipeline RAG (predictions.csv / .json)
  dan membandingkannya dengan benchmark_queries.csv serta ground_truth.csv.
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Set, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_doc_list(val: Any) -> List[str]:
    """Mengubah string daftar dokumen (dipisahkan ';' atau JSON list) menjadi Python list."""
    if pd.isna(val) or val is None:
        return []
    val_str = str(val).strip()
    if not val_str or val_str.upper() == "NONE":
        return []
    if val_str.startswith("[") and val_str.endswith("]"):
        try:
            return [str(x).strip() for x in json.loads(val_str) if str(x).strip()]
        except json.JSONDecodeError:
            pass
    return [x.strip() for x in val_str.split(";") if x.strip()]


def parse_score_list(val: Any) -> List[float]:
    """Mengubah string daftar skor cosine similarity menjadi list float."""
    if pd.isna(val) or val is None:
        return []
    val_str = str(val).strip()
    if not val_str or val_str.upper() == "NONE":
        return []
    if val_str.startswith("[") and val_str.endswith("]"):
        try:
            return [float(x) for x in json.loads(val_str)]
        except (json.JSONDecodeError, ValueError):
            pass
    scores = []
    for x in val_str.split(";"):
        if x.strip():
            try:
                scores.append(float(x.strip()))
            except ValueError:
                continue
    return scores


def precision_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
    """Menghitung Precision@K untuk satu query in-domain."""
    if k <= 0:
        return 0.0
    top_k = retrieved_docs[:k]
    if not top_k:
        return 0.0
    relevant_in_top_k = sum(1 for doc in top_k if doc in relevant_docs)
    return relevant_in_top_k / k


def recall_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
    """Menghitung Recall@K untuk satu query in-domain."""
    if not relevant_docs or k <= 0:
        return 0.0
    top_k = retrieved_docs[:k]
    relevant_in_top_k = sum(1 for doc in top_k if doc in relevant_docs)
    return relevant_in_top_k / len(relevant_docs)


def reciprocal_rank(retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
    """Menghitung Reciprocal Rank (RR) untuk satu query in-domain."""
    for idx, doc in enumerate(retrieved_docs, start=1):
        if doc in relevant_docs:
            return 1.0 / idx
    return 0.0


def compute_ood_metrics(df_merged: pd.DataFrame) -> Dict[str, float]:
    """
    Menghitung OOD Rejection Precision, Recall, dan False Rejection Rate.
    Definisi Positif (P) pada konteks penolakan: Query adalah Out-of-Domain (is_ood == True).
    - True Positive (TP): Query adalah OOD dan sistem berhasil menolak (is_rejected == True).
    - False Positive (FP): Query adalah In-Domain (bukan OOD), tetapi sistem salah menolak (is_rejected == True).
    - False Negative (FN): Query adalah OOD, tetapi sistem gagal menolak / tetap menjawab (is_rejected == False).
    - True Negative (TN): Query adalah In-Domain dan sistem tidak menolak (is_rejected == False).
    """
    is_ood = df_merged["is_ood"].astype(bool)
    is_rejected = df_merged["is_rejected"].astype(bool)

    tp = int(((is_ood == True) & (is_rejected == True)).sum())
    fp = int(((is_ood == False) & (is_rejected == True)).sum())
    fn = int(((is_ood == True) & (is_rejected == False)).sum())
    tn = int(((is_ood == False) & (is_rejected == False)).sum())

    ood_precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    ood_recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    ood_f1 = (2 * ood_precision * ood_recall / (ood_precision + ood_recall)) if (ood_precision + ood_recall) > 0 else 0.0

    return {
        "TP_ood_rejected": tp,
        "FP_indomain_falsely_rejected": fp,
        "FN_ood_missed": fn,
        "TN_indomain_accepted": tn,
        "ood_rejection_precision": ood_precision,
        "ood_rejection_recall": ood_recall,
        "ood_rejection_f1": ood_f1,
    }


def analyze_cosine_similarity(df_merged: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """
    Menganalisis distribusi skor Top-1 Cosine Similarity per kategori query
    (business, synonym, ambiguous, out_of_domain) dan membuat visualisasi.
    """
    df_merged["top1_score"] = df_merged["parsed_scores"].apply(lambda s: s[0] if len(s) > 0 else np.nan)
    stats = (
        df_merged.groupby("category")["top1_score"]
        .agg(["count", "mean", "std", "min", "median", "max"])
        .reset_index()
    )

    os.makedirs(output_dir, exist_ok=True)
    stats.to_csv(os.path.join(output_dir, "cosine_similarity_summary.csv"), index=False)

    # Buat visualisasi jika terdapat skor yang valid
    valid_scores = df_merged.dropna(subset=["top1_score"])
    if not valid_scores.empty:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        # 1. Boxplot Top-1 Cosine Similarity per Kategori Query
        categories = ["business", "synonym", "ambiguous", "out_of_domain"]
        present_cats = [c for c in categories if c in valid_scores["category"].unique()]
        data_by_cat = [valid_scores[valid_scores["category"] == c]["top1_score"].values for c in present_cats]

        if data_by_cat:
            axes[0].boxplot(data_by_cat, patch_artist=True)
            axes[0].set_xticks(range(1, len(present_cats) + 1))
            axes[0].set_xticklabels(present_cats)
            axes[0].set_title("Distribusi Top-1 Cosine Similarity per Kategori")
            axes[0].set_xlabel("Kategori Query")
            axes[0].set_ylabel("Top-1 Cosine Similarity")
            axes[0].grid(axis="y", linestyle="--", alpha=0.6)

        # 2. Histogram In-Domain vs Out-of-Domain untuk Penentuan Threshold
        in_domain_scores = valid_scores[~valid_scores["is_ood"]]["top1_score"]
        ood_scores = valid_scores[valid_scores["is_ood"]]["top1_score"]

        axes[1].hist(in_domain_scores, bins=10, alpha=0.6, label="In-Domain", density=False)
        axes[1].hist(ood_scores, bins=10, alpha=0.6, label="Out-of-Domain (OOD)", density=False)
        axes[1].set_title("Separabilitas Skor: In-Domain vs OOD")
        axes[1].set_xlabel("Top-1 Cosine Similarity")
        axes[1].set_ylabel("Frekuensi Query")
        axes[1].legend()
        axes[1].grid(axis="y", linestyle="--", alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "cosine_similarity_analysis.png"), dpi=200)
        plt.close()

    return stats


def evaluate_predictions(
    queries_path: str,
    gt_path: str | None,
    preds_path: str,
    k_values: List[int],
    output_dir: str,
) -> None:
    """Fungsi utama untuk mengevaluasi prediksi RAG terhadap ground truth."""
    if queries_path.lower().endswith(".json"):
        query_data = json.loads(Path(queries_path).read_text(encoding="utf-8"))["queries"]
        df_q = pd.DataFrame(
            [
                {
                    "query_id": row["id"],
                    "category": row["type"],
                    "query_text": row["query"],
                }
                for row in query_data
            ]
        )
        df_gt = pd.DataFrame(
            [
                {
                    "query_id": row["id"],
                    "relevant_doc_ids": ";".join(row["expected_docs"]),
                    "is_ood": row["type"] == "out_of_domain",
                }
                for row in query_data
            ]
        )
    else:
        if gt_path is None:
            raise ValueError("--gt wajib diisi jika --queries bukan JSON.")
        df_q = pd.read_csv(queries_path)
        df_gt = pd.read_csv(gt_path)
    df_pred = pd.read_csv(preds_path)

    for name, frame in (("queries", df_q), ("ground truth", df_gt), ("predictions", df_pred)):
        if frame["query_id"].duplicated().any():
            raise ValueError(f"ID kueri duplikat pada berkas {name}.")
    query_ids = set(df_q["query_id"])
    if query_ids != set(df_gt["query_id"]) or query_ids != set(df_pred["query_id"]):
        raise ValueError("ID kueri pada query, ground truth, dan predictions harus sama persis.")

    df = (
        df_q.merge(df_gt, on="query_id", how="inner", validate="one_to_one")
        .merge(df_pred, on="query_id", how="inner", validate="one_to_one")
    )

    df["parsed_relevant"] = df["relevant_doc_ids"].apply(lambda x: set(parse_doc_list(x)))
    df["parsed_retrieved"] = df["retrieved_doc_ids"].apply(parse_doc_list)
    df["parsed_scores"] = df["cosine_scores"].apply(parse_score_list)

    # Hitung metrik per baris untuk query In-Domain
    df["rr"] = df.apply(
        lambda r: reciprocal_rank(r["parsed_retrieved"], r["parsed_relevant"]) if not r["is_ood"] else np.nan,
        axis=1,
    )

    for k in k_values:
        df[f"P@{k}"] = df.apply(
            lambda r: precision_at_k(r["parsed_retrieved"], r["parsed_relevant"], k) if not r["is_ood"] else np.nan,
            axis=1,
        )
        df[f"R@{k}"] = df.apply(
            lambda r: recall_at_k(r["parsed_retrieved"], r["parsed_relevant"], k) if not r["is_ood"] else np.nan,
            axis=1,
        )

    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "per_query_evaluation.csv"), index=False)

    # Rekapitulasi metrik retrieval berdasarkan kategori In-Domain
    indomain_df = df[~df["is_ood"]]
    metric_cols = [f"P@{k}" for k in k_values] + [f"R@{k}" for k in k_values] + ["rr"]
    summary_by_cat = indomain_df.groupby("category")[metric_cols].mean().reset_index()
    summary_by_cat = summary_by_cat.rename(columns={"rr": "MRR"})

    overall_row = {"category": "ALL_IN_DOMAIN"}
    for col in metric_cols:
        overall_row[col if col != "rr" else "MRR"] = indomain_df[col].mean()
    summary_by_cat = pd.concat([summary_by_cat, pd.DataFrame([overall_row])], ignore_index=True)
    summary_by_cat.to_csv(os.path.join(output_dir, "retrieval_metrics_summary.csv"), index=False)

    # Evaluasi OOD Rejection
    ood_metrics = compute_ood_metrics(df)
    with open(os.path.join(output_dir, "ood_metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(ood_metrics, f, indent=2)

    # Analisis Cosine Similarity
    cosine_stats = analyze_cosine_similarity(df, output_dir)

    print("=== RINGKASAN METRIK RETRIEVAL (IN-DOMAIN) ===")
    print(summary_by_cat.to_string(index=False))
    print("\n=== RINGKASAN METRIK OOD REJECTION ===")
    for k_name, v_val in ood_metrics.items():
        print(f"{k_name}: {v_val:.4f}" if isinstance(v_val, float) else f"{k_name}: {v_val}")
    print("\n=== STATISTIK TOP-1 COSINE SIMILARITY ===")
    print(cosine_stats.to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluasi Benchmark SmartStore AI T03")
    parser.add_argument("--queries", default="data/benchmark_queries.json", help="Kueri JSON resmi atau ekspor CSV")
    parser.add_argument("--gt", default=None, help="Ground truth CSV untuk kompatibilitas input CSV lama")
    parser.add_argument("--preds", required=True, help="Path ke file predictions.csv dari pipeline RAG T01/T02")
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5], help="Daftar nilai K untuk Precision@K dan Recall@K")
    parser.add_argument("--out", default="eval_results", help="Folder output hasil evaluasi")
    args = parser.parse_args()

    evaluate_predictions(args.queries, args.gt, args.preds, args.k, args.out)
