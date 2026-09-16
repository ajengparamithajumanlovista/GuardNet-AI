from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# GUARDNET-AI
# RESEARCH DATASET PIPELINE
#
# Tujuan:
# 1. Membaca dataset penelitian
# 2. Memeriksa kualitas dataset
# 3. Membandingkan anotasi A1 dan A2
# 4. Menghasilkan statistik dataset
# 5. TIDAK mengarang ground truth
# 6. TIDAK menggunakan provisional_label sebagai ground truth
# 7. Menolak menghitung performa model jika ground truth belum valid
# ============================================================


ROOT = Path(__file__).resolve().parent

DATASET_FILE = ROOT / "dataset_master.csv"
ANNOTATION_DIR = ROOT / "annotations"

A1_FILE = ANNOTATION_DIR / "A1_annotations.csv"
A2_FILE = ANNOTATION_DIR / "A2_annotations.csv"

REPORT_FILE = ROOT / "research_pipeline_report.txt"


VALID_LABELS = {"C0", "C1", "C2"}


# ============================================================
# UTILITIES
# ============================================================

def read_csv(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def percentage(part, total):
    if total == 0:
        return 0.0
    return part / total * 100.0


# ============================================================
# DATASET
# ============================================================

def analyse_dataset(rows):

    result = {}

    sample_ids = [
        clean(row.get("sample_id"))
        for row in rows
    ]

    sample_ids = [
        x for x in sample_ids if x
    ]

    result["total"] = len(rows)

    result["unique_sample_ids"] = len(
        set(sample_ids)
    )

    result["duplicate_sample_ids"] = (
        len(sample_ids) -
        len(set(sample_ids))
    )

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    result["source_type"] = Counter(
        clean(row.get("source_type"))
        for row in rows
    )

    # --------------------------------------------------------
    # CONTENT TYPE
    # --------------------------------------------------------

    result["content_type"] = Counter(
        clean(row.get("content_type"))
        for row in rows
    )

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    accounts = [
        clean(row.get("account_id"))
        for row in rows
    ]

    accounts = [
        x for x in accounts if x
    ]

    result["unique_accounts"] = len(set(accounts))

    result["duplicate_accounts"] = (
        len(accounts) -
        len(set(accounts))
    )

    # --------------------------------------------------------
    # MODALITY
    # --------------------------------------------------------

    modality_columns = {
        "image": "image_available",
        "ocr": "ocr_available",
        "visual": "visual_available",
        "audio_asr": "audio_available",
    }

    result["modalities"] = {}

    for name, column in modality_columns.items():

        available = sum(
            clean(row.get(column)) == "1"
            for row in rows
        )

        result["modalities"][name] = {
            "available": available,
            "missing": len(rows) - available,
            "availability_percent":
                percentage(available, len(rows))
        }

    # --------------------------------------------------------
    # PROVISIONAL LABEL
    # --------------------------------------------------------

    result["provisional_label"] = Counter(
        clean(row.get("provisional_label")).upper()
        for row in rows
        if clean(row.get("provisional_label"))
    )

    return result


# ============================================================
# ANNOTATION
# ============================================================

def load_annotation(path):

    if not path.exists():
        return {}

    rows = read_csv(path)

    annotations = {}

    for row in rows:

        sample_id = clean(
            row.get("sample_id")
        )

        label = clean(
            row.get("label")
        ).upper()

        if not sample_id:
            continue

        annotations[sample_id] = {
            "label": label,
            "notes": clean(
                row.get("notes")
            )
        }

    return annotations


def analyse_annotations(dataset_rows, a1, a2):

    sample_ids = [
        clean(row.get("sample_id"))
        for row in dataset_rows
    ]

    both_valid = []
    agreements = []
    disagreements = []

    for sample_id in sample_ids:

        label_a1 = a1.get(
            sample_id,
            {}
        ).get("label", "")

        label_a2 = a2.get(
            sample_id,
            {}
        ).get("label", "")

        if (
            label_a1 in VALID_LABELS
            and
            label_a2 in VALID_LABELS
        ):

            both_valid.append(sample_id)

            if label_a1 == label_a2:
                agreements.append(sample_id)
            else:
                disagreements.append({
                    "sample_id": sample_id,
                    "A1": label_a1,
                    "A2": label_a2
                })

    result = {}

    result["samples_with_two_valid_annotations"] = len(
        both_valid
    )

    result["agreements"] = len(
        agreements
    )

    result["disagreements"] = len(
        disagreements
    )

    if both_valid:
        result["observed_agreement"] = (
            len(agreements) /
            len(both_valid)
        )
    else:
        result["observed_agreement"] = None

    result["a1_distribution"] = Counter(
        a1[s]["label"]
        for s in both_valid
    )

    result["a2_distribution"] = Counter(
        a2[s]["label"]
        for s in both_valid
    )

    result["disagreements_detail"] = disagreements

    # --------------------------------------------------------
    # KAPPA STATUS
    #
    # Cohen's kappa membutuhkan variasi kategori yang
    # memadai. Jika kedua annotator hanya menggunakan satu
    # kategori, kappa tidak informatif / undefined.
    # --------------------------------------------------------

    all_labels = set()

    for sample_id in both_valid:
        all_labels.add(a1[sample_id]["label"])
        all_labels.add(a2[sample_id]["label"])

    if len(all_labels) < 2:

        result["cohens_kappa"] = None

        result["kappa_status"] = (
            "UNDEFINED_OR_NOT_INFORMATIVE: "
            "hanya satu kategori digunakan oleh "
            "kedua annotator."
        )

    else:

        result["cohens_kappa"] = (
            calculate_cohens_kappa(
                [
                    a1[s]["label"]
                    for s in both_valid
                ],
                [
                    a2[s]["label"]
                    for s in both_valid
                ]
            )
        )

        result["kappa_status"] = "CALCULATED"

    return result


# ============================================================
# COHEN KAPPA
# ============================================================

def calculate_cohens_kappa(labels_a, labels_b):

    n = len(labels_a)

    if n == 0:
        return None

    observed = sum(
        a == b
        for a, b in zip(
            labels_a,
            labels_b
        )
    ) / n

    categories = sorted(
        set(labels_a) |
        set(labels_b)
    )

    count_a = Counter(labels_a)
    count_b = Counter(labels_b)

    expected = 0.0

    for category in categories:

        p_a = count_a[category] / n
        p_b = count_b[category] / n

        expected += p_a * p_b

    denominator = 1.0 - expected

    if abs(denominator) < 1e-12:
        return None

    return (
        observed - expected
    ) / denominator


# ============================================================
# PROVISIONAL VS HUMAN
# ============================================================

def compare_provisional_to_human(
    dataset_rows,
    a1,
    a2
):

    result = []

    for row in dataset_rows:

        sample_id = clean(
            row.get("sample_id")
        )

        provisional = clean(
            row.get("provisional_label")
        ).upper()

        human_a1 = a1.get(
            sample_id,
            {}
        ).get("label", "")
        
        human_a2 = a2.get(
            sample_id,
            {}
        ).get("label", "")

        result.append({
            "sample_id": sample_id,
            "provisional": provisional,
            "A1": human_a1,
            "A2": human_a2,
            "provisional_equals_A1":
                provisional == human_a1
                if provisional and human_a1
                else False,
            "provisional_equals_A2":
                provisional == human_a2
                if provisional and human_a2
                else False
        })

    return result


# ============================================================
# REPORT
# ============================================================

def write_report(
    dataset_result,
    annotation_result,
    comparison
):

    lines = []

    lines.append("=" * 72)
    lines.append(
        "GUARDNET-AI — RESEARCH PIPELINE AUDIT"
    )
    lines.append("=" * 72)
    lines.append("")

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    lines.append(
        "1. DATASET CHARACTERISTICS"
    )
    lines.append("-" * 72)

    lines.append(
        f"Total content units: "
        f"{dataset_result['total']}"
    )

    lines.append(
        f"Unique sample IDs: "
        f"{dataset_result['unique_sample_ids']}"
    )

    lines.append(
        f"Duplicate sample IDs: "
        f"{dataset_result['duplicate_sample_ids']}"
    )

    lines.append("")

    lines.append("Source type:")

    for key, value in dataset_result[
        "source_type"
    ].items():

        lines.append(
            f"  {key}: {value} "
            f"({percentage(value, dataset_result['total']):.2f}%)"
        )

    lines.append("")

    lines.append("Content type:")

    for key, value in dataset_result[
        "content_type"
    ].items():

        lines.append(
            f"  {key}: {value} "
            f"({percentage(value, dataset_result['total']):.2f}%)"
        )

    lines.append("")

    lines.append(
        f"Unique accounts: "
        f"{dataset_result['unique_accounts']}"
    )

    lines.append(
        f"Duplicate account occurrences: "
        f"{dataset_result['duplicate_accounts']}"
    )

    lines.append("")

    lines.append("Modalities:")

    for name, data in dataset_result[
        "modalities"
    ].items():

        lines.append(
            f"  {name}: "
            f"{data['available']} available, "
            f"{data['missing']} missing "
            f"({data['availability_percent']:.2f}% available)"
        )

    lines.append("")

    lines.append(
        "Provisional label distribution:"
    )

    for label in sorted(
        VALID_LABELS
    ):

        value = dataset_result[
            "provisional_label"
        ].get(label, 0)

        lines.append(
            f"  {label}: {value}"
        )

    lines.append("")

    # --------------------------------------------------------
    # ANNOTATION
    # --------------------------------------------------------

    lines.append(
        "2. ANNOTATION QUALITY"
    )
    lines.append("-" * 72)

    lines.append(
        "Samples with two valid annotations: "
        f"{annotation_result['samples_with_two_valid_annotations']}"
    )

    if annotation_result[
        "observed_agreement"
    ] is not None:

        lines.append(
            "Observed agreement: "
            f"{annotation_result['observed_agreement'] * 100:.2f}%"
        )

    else:

        lines.append(
            "Observed agreement: NOT AVAILABLE"
        )

    if annotation_result[
        "cohens_kappa"
    ] is None:

        lines.append(
            "Cohen's Kappa: NOT INFORMATIVE / UNDEFINED"
        )

    else:

        lines.append(
            "Cohen's Kappa: "
            f"{annotation_result['cohens_kappa']:.6f}"
        )

    lines.append(
        "Kappa status: "
        f"{annotation_result['kappa_status']}"
    )

    lines.append(
        "Agreements: "
        f"{annotation_result['agreements']}"
    )

    lines.append(
        "Disagreements: "
        f"{annotation_result['disagreements']}"
    )

    lines.append("")

    lines.append(
        "A1 distribution:"
    )

    for label in sorted(VALID_LABELS):

        lines.append(
            f"  {label}: "
            f"{annotation_result['a1_distribution'].get(label, 0)}"
        )

    lines.append("")

    lines.append(
        "A2 distribution:"
    )

    for label in sorted(VALID_LABELS):

        lines.append(
            f"  {label}: "
            f"{annotation_result['a2_distribution'].get(label, 0)}"
        )

    lines.append("")

    # --------------------------------------------------------
    # PROVISIONAL COMPARISON
    # --------------------------------------------------------

    mismatch_count = sum(
        not (
            item["provisional_equals_A1"]
            and
            item["provisional_equals_A2"]
        )
        for item in comparison
    )

    lines.append(
        "3. PROVISIONAL LABEL VS HUMAN ANNOTATION"
    )
    lines.append("-" * 72)

    lines.append(
        f"Samples checked: {len(comparison)}"
    )

    lines.append(
        f"Samples where provisional label differs "
        f"from at least one human annotation: "
        f"{mismatch_count}"
    )

    lines.append("")

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    lines.append(
        "4. RESEARCH DECISION"
    )
    lines.append("-" * 72)

    if mismatch_count > 0:

        lines.append(
            "STATUS: PILOT DATA REQUIRES QUALITY CONTROL."
        )

        lines.append(
            "Provisional labels MUST NOT be promoted "
            "to final ground truth."
        )

    elif annotation_result[
        "samples_with_two_valid_annotations"
    ] < dataset_result["total"]:

        lines.append(
            "STATUS: ANNOTATION INCOMPLETE."
        )

    elif annotation_result[
        "cohens_kappa"
    ] is None:

        lines.append(
            "STATUS: ANNOTATION VARIATION INSUFFICIENT "
            "FOR INFORMATIVE KAPPA."
        )

    else:

        lines.append(
            "STATUS: ANNOTATION READY FOR FURTHER "
            "GROUND-TRUTH REVIEW."
        )

    lines.append("")

    lines.append(
        "IMPORTANT:"
    )

    lines.append(
        "- This report does not fabricate metrics."
    )

    lines.append(
        "- Provisional labels are not ground truth."
    )

    lines.append(
        "- Model predictions must not be used as ground truth."
    )

    lines.append(
        "- Final train/validation/test counts require "
        "final adjudicated labels."
    )

    lines.append("")

    lines.append("=" * 72)
    lines.append("END OF REPORT")
    lines.append("=" * 72)

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print(
        "GUARDNET-AI — RESEARCH PIPELINE AUDIT"
    )
    print("=" * 72)

    dataset = read_csv(
        DATASET_FILE
    )

    a1 = load_annotation(
        A1_FILE
    )

    a2 = load_annotation(
        A2_FILE
    )

    dataset_result = analyse_dataset(
        dataset
    )

    annotation_result = analyse_annotations(
        dataset,
        a1,
        a2
    )

    comparison = compare_provisional_to_human(
        dataset,
        a1,
        a2
    )

    report = write_report(
        dataset_result,
        annotation_result,
        comparison
    )

    print()
    print(report)

    print()
    print(
        "Report saved to:"
    )
    print(
        REPORT_FILE
    )
    print()


if __name__ == "__main__":
    main()