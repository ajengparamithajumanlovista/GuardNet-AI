# ============================================================
# GUARDNET-AI FINAL ANNOTATION MERGER
#
# Input:
#   annotations/A1_annotations.csv
#   annotations/A2_annotations.csv
#   dataset_master.csv
#
# Output:
#   final_ground_truth.csv
#   annotation_quality_report.txt
#
# Cohen's Kappa is calculated only from complete independent
# A1/A2 annotations. No model prediction is used.
# ============================================================

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset_master.csv"
A1_FILE = ROOT / "annotations" / "A1_annotations.csv"
A2_FILE = ROOT / "annotations" / "A2_annotations.csv"
FINAL_FILE = ROOT / "final_ground_truth.csv"
REPORT_FILE = ROOT / "annotation_quality_report.txt"

LABELS = ("C0", "C1", "C2")


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def kappa(a1, a2):
    n = len(a1)
    if n == 0:
        return None

    observed = sum(x == y for x, y in zip(a1, a2)) / n
    c1 = Counter(a1)
    c2 = Counter(a2)

    expected = sum(
        (c1[label] / n) * (c2[label] / n)
        for label in LABELS
    )

    if 1 - expected == 0:
        return 1.0

    return (observed - expected) / (1 - expected)


def main():
    dataset = read_csv(DATASET)
    a1_rows = {r["sample_id"]: r for r in read_csv(A1_FILE)}
    a2_rows = {r["sample_id"]: r for r in read_csv(A2_FILE)}

    final_rows = []
    paired_a1 = []
    paired_a2 = []
    disagreements = []

    for row in dataset:
        sid = row.get("sample_id", "")
        x = a1_rows.get(sid, {}).get("label", "")
        y = a2_rows.get(sid, {}).get("label", "")

        if x in LABELS and y in LABELS:
            paired_a1.append(x)
            paired_a2.append(y)

            if x == y:
                final = x
                adjudication = "AGREEMENT"
            else:
                final = ""
                adjudication = "REQUIRED"

                disagreements.append({
                    "sample_id": sid,
                    "annotator_1": x,
                    "annotator_2": y,
                })
        else:
            final = ""
            adjudication = "INCOMPLETE"

        final_rows.append({
            "sample_id": sid,
            "source_type": row.get("source_type", ""),
            "content_type": row.get("content_type", ""),
            "caption": row.get("caption", ""),
            "comments": row.get("comments", ""),
            "account_id": row.get("account_id", ""),
            "annotator_1": x,
            "annotator_2": y,
            "adjudication": adjudication,
            "final_label": final,
        })

    with FINAL_FILE.open("w", encoding="utf-8", newline="") as f:
        fields = list(final_rows[0].keys()) if final_rows else []
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(final_rows)

    n = len(paired_a1)
    agreement = (
        sum(x == y for x, y in zip(paired_a1, paired_a2)) / n
        if n else None
    )
    kap = kappa(paired_a1, paired_a2)

    lines = [
        "=" * 70,
        "GUARDNET-AI — ANNOTATION QUALITY REPORT",
        "=" * 70,
        f"Total dataset: {len(dataset)}",
        f"Complete A1/A2 pairs: {n}",
        f"Observed agreement: "
        f"{agreement * 100:.2f}%" if agreement is not None
        else "Observed agreement: NOT AVAILABLE",
        f"Cohen's Kappa: {kap:.4f}" if kap is not None
        else "Cohen's Kappa: NOT AVAILABLE",
        f"Disagreements: {len(disagreements)}",
        "",
        "IMPORTANT:",
        "A disagreement has no final_label until human adjudication.",
        "Do not fill it from GuardNet-AI prediction.",
        "",
        "Final ground truth is complete only when every sample has",
        "a final_label after agreement or adjudication.",
        "=" * 70,
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print()
    print("Output:")
    print(FINAL_FILE)
    print(REPORT_FILE)


if __name__ == "__main__":
    main()
