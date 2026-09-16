# ============================================================
# GUARDNET-AI RESEARCH PUBLICATION EDITION
# FINAL DATASET / ANNOTATION ANALYSIS TOOL
#
# PURPOSE
# 1. Validate the research dataset schema.
# 2. Report dataset characteristics.
# 3. Check class distribution.
# 4. Check account-disjoint readiness.
# 5. Calculate Cohen's Kappa when two independent annotations
#    are actually present.
# 6. List disagreements for adjudication.
#
# IMPORTANT:
# This script NEVER invents research results.
# If annotation fields are empty, Cohen's Kappa is reported as
# "NOT AVAILABLE" rather than fabricated.
# ============================================================

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset_master.csv"
REPORT = ROOT / "dataset_analysis_report.txt"

LABELS = ("C0", "C1", "C2")

LABEL_NAMES = {
    "C0": "Non-Gambling",
    "C1": "Gambling-Related Non-Promotion",
    "C2": "Gambling Promotion",
}

REQUIRED_COLUMNS = {
    "sample_id",
    "source_type",
    "content_type",
    "caption",
    "comments",
    "image_available",
    "ocr_available",
    "visual_available",
    "audio_available",
    "account_id",
    "annotator_1",
    "annotator_2",
    "final_label",
}


def clean(value) -> str:
    return str(value or "").strip()


def read_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"FILE TIDAK DITEMUKAN:\n{path}\n\n"
            "Pastikan dataset_master.csv berada di folder research."
        )

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = set(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(
            "KOLOM DATASET BELUM LENGKAP.\n"
            f"Kolom yang hilang: {', '.join(sorted(missing))}"
        )

    return rows


def pct(n, total):
    return (n / total * 100.0) if total else 0.0


def parse_bool(value):
    v = clean(value).lower()
    return v in {"1", "true", "yes", "y"}


def validate_rows(rows):
    errors = []
    warnings = []

    sample_ids = Counter()
    accounts = Counter()

    for i, row in enumerate(rows, start=2):
        sid = clean(row.get("sample_id"))
        account = clean(row.get("account_id"))

        if not sid:
            errors.append(f"Baris {i}: sample_id kosong.")
        else:
            sample_ids[sid] += 1

        if not account:
            warnings.append(
                f"Baris {i} ({sid or 'NO-ID'}): account_id kosong; "
                "account-disjoint split belum dapat diverifikasi."
            )
        else:
            accounts[account] += 1

        # Only final labels are allowed to become ground truth.
        final_label = clean(row.get("final_label")).upper()
        if final_label and final_label not in LABELS:
            errors.append(
                f"Baris {i} ({sid}): final_label '{final_label}' "
                f"bukan salah satu dari {LABELS}."
            )

        for field in ("annotator_1", "annotator_2"):
            label = clean(row.get(field)).upper()
            if label and label not in LABELS:
                errors.append(
                    f"Baris {i} ({sid}): {field} '{label}' "
                    f"bukan salah satu dari {LABELS}."
                )

        # A final label should not be silently present when two
        # annotators disagree and no adjudication evidence exists.
        a1 = clean(row.get("annotator_1")).upper()
        a2 = clean(row.get("annotator_2")).upper()
        final = final_label
        if a1 and a2 and a1 != a2 and final:
            adjudication = clean(row.get("adjudication"))
            if not adjudication:
                warnings.append(
                    f"Baris {i} ({sid}): A1={a1}, A2={a2}, "
                    "tetapi final_label sudah diisi tanpa catatan adjudication."
                )

    duplicate_ids = {
        sid: n for sid, n in sample_ids.items() if n > 1
    }

    return errors, warnings, duplicate_ids, accounts


def kappa(a1, a2):
    if not a1 or len(a1) != len(a2):
        return None

    n = len(a1)
    observed = sum(x == y for x, y in zip(a1, a2)) / n

    ca = Counter(a1)
    cb = Counter(a2)

    expected = sum(
        (ca[label] / n) * (cb[label] / n)
        for label in LABELS
    )

    if math.isclose(1.0 - expected, 0.0):
        return 1.0

    return (observed - expected) / (1.0 - expected)


def kappa_interpretation(value):
    if value is None:
        return "Belum dapat dihitung."

    # Common Landis-Koch descriptive scale.
    if value < 0:
        return "Poor"
    if value < 0.20:
        return "Slight"
    if value < 0.40:
        return "Fair"
    if value < 0.60:
        return "Moderate"
    if value < 0.80:
        return "Substantial"
    return "Almost perfect"


def analyze(rows):
    total = len(rows)

    final_labels = Counter()
    provisional_labels = Counter()
    source_types = Counter()
    content_types = Counter()

    modalities = Counter()
    accounts = Counter()

    a1 = []
    a2 = []
    disagreements = []

    for row in rows:
        final = clean(row.get("final_label")).upper()
        if final in LABELS:
            final_labels[final] += 1

        provisional = clean(row.get("provisional_label")).upper()
        if provisional in LABELS:
            provisional_labels[provisional] += 1

        source_types[clean(row.get("source_type")) or "UNKNOWN"] += 1
        content_types[clean(row.get("content_type")) or "UNKNOWN"] += 1

        account = clean(row.get("account_id"))
        if account:
            accounts[account] += 1

        for field, name in (
            ("image_available", "image"),
            ("ocr_available", "ocr"),
            ("visual_available", "visual"),
            ("audio_available", "audio_asr"),
        ):
            if parse_bool(row.get(field)):
                modalities[name] += 1

        x = clean(row.get("annotator_1")).upper()
        y = clean(row.get("annotator_2")).upper()

        if x in LABELS and y in LABELS:
            a1.append(x)
            a2.append(y)

            if x != y:
                disagreements.append({
                    "sample_id": clean(row.get("sample_id")),
                    "annotator_1": x,
                    "annotator_2": y,
                    "text": clean(row.get("caption")),
                    "adjudication": clean(row.get("adjudication")),
                    "final_label": clean(row.get("final_label")).upper(),
                })

    agreement = None
    kap = None

    if a1:
        agreement = sum(
            x == y for x, y in zip(a1, a2)
        ) / len(a1)
        kap = kappa(a1, a2)

    return {
        "total": total,
        "final_labels": final_labels,
        "provisional_labels": provisional_labels,
        "source_types": source_types,
        "content_types": content_types,
        "modalities": modalities,
        "accounts": accounts,
        "annotation_n": len(a1),
        "agreement": agreement,
        "kappa": kap,
        "kappa_interpretation": kappa_interpretation(kap),
        "disagreements": disagreements,
    }


def build_report(rows, result, errors, warnings, duplicate_ids):
    lines = []

    add = lines.append

    add("=" * 72)
    add("GUARDNET-AI — FINAL RESEARCH DATASET REPORT")
    add("=" * 72)
    add("")
    add("STATUS: DATA-DRIVEN REPORT — NO FABRICATED METRICS")
    add("")

    add("1. DATASET CHARACTERISTICS")
    add("-" * 72)
    add(f"Total content units: {result['total']}")
    add("")

    add("Final ground-truth distribution:")
    if sum(result["final_labels"].values()) == 0:
        add("  BELUM TERSEDIA — final_label belum diisi.")
    else:
        for label in LABELS:
            n = result["final_labels"][label]
            add(
                f"  {label} — {LABEL_NAMES[label]}: "
                f"{n} ({pct(n, result['total']):.2f}%)"
            )

    add("")
    add("Source type:")
    for key, n in sorted(result["source_types"].items()):
        add(f"  {key}: {n} ({pct(n, result['total']):.2f}%)")

    add("")
    add("Content type:")
    for key, n in sorted(result["content_types"].items()):
        add(f"  {key}: {n} ({pct(n, result['total']):.2f}%)")

    add("")
    add("Modalities available:")
    for name in ("image", "ocr", "visual", "audio_asr"):
        n = result["modalities"][name]
        add(f"  {name}: {n} ({pct(n, result['total']):.2f}%)")

    add("")
    add(f"Unique accounts: {len(result['accounts'])}")

    if duplicate_ids:
        add("")
        add("DUPLICATE SAMPLE IDs:")
        for sid, n in sorted(duplicate_ids.items()):
            add(f"  {sid}: {n} occurrences")

    add("")
    add("2. ANNOTATION QUALITY")
    add("-" * 72)
    add(
        f"Samples with two valid independent annotations: "
        f"{result['annotation_n']}"
    )

    if result["agreement"] is None:
        add("Observed agreement: NOT AVAILABLE")
        add("Cohen's Kappa: NOT AVAILABLE")
        add(
            "Interpretation: Isi annotator_1 dan annotator_2 "
            "setelah anotasi independen."
        )
    else:
        add(
            f"Observed agreement: "
            f"{result['agreement'] * 100:.2f}%"
        )
        add(
            f"Cohen's Kappa: {result['kappa']:.4f}"
        )
        add(
            f"Interpretation: {result['kappa_interpretation']}"
        )

    add("")
    add(
        f"Disagreements requiring adjudication: "
        f"{len(result['disagreements'])}"
    )

    for d in result["disagreements"]:
        add(
            f"  {d['sample_id']}: "
            f"A1={d['annotator_1']} | "
            f"A2={d['annotator_2']} | "
            f"final={d['final_label'] or 'EMPTY'}"
        )

    add("")
    add("3. DATA QUALITY VALIDATION")
    add("-" * 72)

    if errors:
        add(f"ERRORS: {len(errors)}")
        for e in errors:
            add(f"  - {e}")
    else:
        add("Errors: 0")

    add("")

    if warnings:
        add(f"WARNINGS: {len(warnings)}")
        for w in warnings:
            add(f"  - {w}")
    else:
        add("Warnings: 0")

    add("")
    add("4. RESEARCH SAFETY CHECKS")
    add("-" * 72)
    add(
        "Ground truth must come from adjudicated human annotation, "
        "not from GuardNet-AI predictions."
    )
    add(
        "Pilot/test data must not be reported as final model performance."
    )
    add(
        "Training/validation/testing must preserve account-disjoint "
        "evaluation according to the research protocol."
    )
    add(
        "All final claims must be generated from the actual collected dataset."
    )
    add("")

    add("5. DATASET PROTOCOL ALIGNMENT")
    add("-" * 72)
    add("Target minimum content units in the proposal: 3,000 unique units.")
    add("Planned split: 70% training / 15% validation / 15% testing.")
    add("Minimum split constraint: account-disjoint.")
    add("Classes: C0, C1, C2.")
    add("Annotation: at least two independent annotators.")
    add("Agreement: Cohen's Kappa.")
    add("Disagreement: adjudication before final ground truth.")
    add("")

    add("=" * 72)
    add("END OF REPORT")
    add("=" * 72)

    return "\n".join(lines)


def main():
    print()
    print("=" * 72)
    print("GUARDNET-AI — FINAL DATASET ANALYSIS")
    print("=" * 72)
    print()

    try:
        rows = read_rows(DATASET)
    except Exception as exc:
        print("[ERROR]")
        print(exc)
        print()
        print("Current expected location:")
        print(DATASET)
        sys.exit(1)

    errors, warnings, duplicate_ids, _ = validate_rows(rows)
    result = analyze(rows)

    report = build_report(
        rows,
        result,
        errors,
        warnings,
        duplicate_ids,
    )

    REPORT.write_text(report, encoding="utf-8")

    print(report)
    print()
    print(f"Report saved to:\n{REPORT}")

    if errors:
        print()
        print(
            "[STATUS] DATASET BELUM VALID. "
            "Perbaiki ERROR sebelum digunakan untuk hasil KTI."
        )
        sys.exit(2)

    print()
    print(
        "[STATUS] Schema valid. "
        "Kelengkapan anotasi dan target dataset tetap harus dipenuhi "
        "sebelum klaim hasil final."
    )


if __name__ == "__main__":
    main()
