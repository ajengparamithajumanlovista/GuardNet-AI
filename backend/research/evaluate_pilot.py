from __future__ import annotations

import csv
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ============================================================
# GUARDNET-AI
# PILOT EVALUATION
#
# IMPORTANT:
# - provisional_label is used ONLY as pilot reference
# - it is NOT final human ground truth
# - results MUST NOT be reported as final performance
# ============================================================


ROOT = Path(__file__).resolve().parent

DATASET_FILE = ROOT / "dataset_master.csv"

RESULT_FILE = ROOT / "pilot_evaluation_results.csv"

REPORT_FILE = ROOT / "pilot_evaluation_report.txt"

API_URL = "http://127.0.0.1:8000/analyze"

VALID_LABELS = {
    "C0",
    "C1",
    "C2",
}


# ============================================================
# CSV
# ============================================================

def load_dataset():

    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {DATASET_FILE}"
        )

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        return list(
            csv.DictReader(f)
        )


# ============================================================
# API
# ============================================================

def call_guardnet(
    text: str,
    caption: str,
    comments: str
):

    payload = {
        "text": text or "",
        "caption": caption or "",
        "comments": (
            [comments]
            if comments
            else []
        ),
    }

    body = json.dumps(
        payload
    ).encode("utf-8")

    request = Request(
        API_URL,
        data=body,
        headers={
            "Content-Type":
                "application/json"
        },
        method="POST"
    )

    start = time.perf_counter()

    try:

        with urlopen(
            request,
            timeout=60
        ) as response:

            raw = response.read()

        elapsed = (
            time.perf_counter()
            - start
        )

        result = json.loads(
            raw.decode("utf-8")
        )

        return result, elapsed * 1000

    except HTTPError as e:

        elapsed = (
            time.perf_counter()
            - start
        )

        raise RuntimeError(
            f"HTTP {e.code}: "
            f"{e.read().decode('utf-8', errors='ignore')}"
        ) from e

    except URLError as e:

        raise RuntimeError(
            "Tidak dapat terhubung ke "
            f"GuardNet-AI API: {e}"
        ) from e


# ============================================================
# RESULT EXTRACTION
# ============================================================

def extract_prediction(result):

    if not isinstance(
        result,
        dict
    ):
        return {
            "label": "ERROR",
            "confidence": 0.0,
            "risk_score": 0.0,
            "status": "invalid_response",
        }

    if result.get("status") == "error":

        return {
            "label": "ERROR",
            "confidence": 0.0,
            "risk_score": 0.0,
            "status": "api_error",
        }

    classification = result.get(
        "classification"
    )

    if not isinstance(
        classification,
        dict
    ):

        classification = result.get(
            "fusion_result",
            {}
        )

    if not isinstance(
        classification,
        dict
    ):

        classification = {}

    label = (
        classification.get("label")
        or classification.get("classification")
        or result.get("label")
        or "C0"
    )

    label = str(
        label
    ).strip().upper()

    confidence = (
        classification.get(
            "confidence"
        )
    )

    if confidence is None:

        confidence = (
            result.get(
                "confidence",
                0.0
            )
        )

    try:

        confidence = float(
            confidence
        )

    except Exception:

        confidence = 0.0

    # If API returns percentage
    if confidence > 1:
        confidence /= 100.0

    risk_score = (
        classification.get(
            "risk_score",
            result.get(
                "risk_score",
                0.0
            )
        )
    )

    try:

        risk_score = float(
            risk_score
        )

    except Exception:

        risk_score = 0.0

    return {
        "label": label,
        "confidence": confidence,
        "risk_score": risk_score,
        "status": "success",
    }


# ============================================================
# CONFUSION MATRIX
# ============================================================

def confusion_matrix(
    y_true,
    y_pred
):

    matrix = {
        actual: {
            predicted: 0
            for predicted in sorted(
                VALID_LABELS
            )
        }
        for actual in sorted(
            VALID_LABELS
        )
    }

    for actual, predicted in zip(
        y_true,
        y_pred
    ):

        if (
            actual in VALID_LABELS
            and
            predicted in VALID_LABELS
        ):

            matrix[
                actual
            ][
                predicted
            ] += 1

    return matrix


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    y_true,
    y_pred
):

    valid_pairs = [
        (a, p)
        for a, p in zip(
            y_true,
            y_pred
        )
        if (
            a in VALID_LABELS
            and
            p in VALID_LABELS
        )
    ]

    if not valid_pairs:

        return {
            "accuracy": None,
            "macro_precision": None,
            "macro_recall": None,
            "macro_f1": None,
            "f1_c2": None,
        }

    true = [
        x[0]
        for x in valid_pairs
    ]

    pred = [
        x[1]
        for x in valid_pairs
    ]

    accuracy = sum(
        a == p
        for a, p in valid_pairs
    ) / len(valid_pairs)

    precisions = []
    recalls = []
    f1s = []

    per_class = {}

    for label in sorted(
        VALID_LABELS
    ):

        tp = sum(
            a == label and p == label
            for a, p in valid_pairs
        )

        fp = sum(
            a != label and p == label
            for a, p in valid_pairs
        )

        fn = sum(
            a == label and p != label
            for a, p in valid_pairs
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp)
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn)
            else 0.0
        )

        if (
            precision + recall
        ):

            f1 = (
                2
                * precision
                * recall
                /
                (
                    precision
                    + recall
                )
            )

        else:

            f1 = 0.0

        precisions.append(
            precision
        )

        recalls.append(
            recall
        )

        f1s.append(
            f1
        )

        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    return {
        "accuracy": accuracy,
        "macro_precision": statistics.mean(
            precisions
        ),
        "macro_recall": statistics.mean(
            recalls
        ),
        "macro_f1": statistics.mean(
            f1s
        ),
        "f1_c2": per_class[
            "C2"
        ]["f1"],
        "per_class": per_class,
    }


# ============================================================
# REPORT
# ============================================================

def write_report(
    rows,
    metrics,
    latencies,
    errors,
    matrix
):

    lines = []

    lines.append(
        "=" * 72
    )

    lines.append(
        "GUARDNET-AI — PILOT EVALUATION REPORT"
    )

    lines.append(
        "=" * 72
    )

    lines.append("")

    lines.append(
        "WARNING:"
    )

    lines.append(
        "This is a PILOT / PRELIMINARY evaluation."
    )

    lines.append(
        "provisional_label is NOT final human ground truth."
    )

    lines.append(
        "Do NOT report these values as final model performance."
    )

    lines.append("")

    lines.append(
        f"Samples evaluated: {len(rows)}"
    )

    lines.append(
        f"Successful predictions: "
        f"{len(rows) - len(errors)}"
    )

    lines.append(
        f"API errors: {len(errors)}"
    )

    lines.append("")

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    lines.append(
        "1. PILOT METRICS"
    )

    lines.append(
        "-" * 72
    )

    if metrics[
        "accuracy"
    ] is not None:

        lines.append(
            f"Accuracy: "
            f"{metrics['accuracy'] * 100:.2f}%"
        )

        lines.append(
            f"Macro Precision: "
            f"{metrics['macro_precision']:.4f}"
        )

        lines.append(
            f"Macro Recall: "
            f"{metrics['macro_recall']:.4f}"
        )

        lines.append(
            f"Macro F1: "
            f"{metrics['macro_f1']:.4f}"
        )

        lines.append(
            f"F1 C2: "
            f"{metrics['f1_c2']:.4f}"
        )

    else:

        lines.append(
            "Metrics unavailable."
        )

    lines.append("")

    # --------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------

    lines.append(
        "2. CONFUSION MATRIX"
    )

    lines.append(
        "-" * 72
    )

    lines.append(
        "Actual \\ Predicted | C0 | C1 | C2"
    )

    for actual in (
        "C0",
        "C1",
        "C2"
    ):

        lines.append(
            f"{actual:18} | "
            f"{matrix[actual]['C0']:2} | "
            f"{matrix[actual]['C1']:2} | "
            f"{matrix[actual]['C2']:2}"
        )

    lines.append("")

    # --------------------------------------------------------
    # LATENCY
    # --------------------------------------------------------

    lines.append(
        "3. LATENCY"
    )

    lines.append(
        "-" * 72
    )

    if latencies:

        ordered = sorted(
            latencies
        )

        p95_index = min(
            len(ordered) - 1,
            max(
                0,
                int(
                    0.95
                    * len(ordered)
                ) - 1
            )
        )

        lines.append(
            f"Mean latency: "
            f"{statistics.mean(latencies):.2f} ms"
        )

        lines.append(
            f"Median latency: "
            f"{statistics.median(latencies):.2f} ms"
        )

        lines.append(
            f"P95 latency: "
            f"{ordered[p95_index]:.2f} ms"
        )

    else:

        lines.append(
            "Latency unavailable."
        )

    lines.append("")

    # --------------------------------------------------------
    # ERRORS
    # --------------------------------------------------------

    lines.append(
        "4. API ERRORS"
    )

    lines.append(
        "-" * 72
    )

    if errors:

        for error in errors:

            lines.append(
                f"{error['sample_id']}: "
                f"{error['error']}"
            )

    else:

        lines.append(
            "None"
        )

    lines.append("")

    lines.append(
        "=" * 72
    )

    lines.append(
        "END OF PILOT REPORT"
    )

    lines.append(
        "=" * 72
    )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print(
        "GUARDNET-AI — PILOT EVALUATION"
    )
    print("=" * 72)

    dataset = load_dataset()

    results = []

    latencies = []

    errors = []

    print(
        f"\nDataset: {DATASET_FILE}"
    )

    print(
        f"Samples: {len(dataset)}"
    )

    print(
        f"API: {API_URL}"
    )

    print()

    for index, row in enumerate(
        dataset,
        start=1
    ):

        sample_id = (
            row.get("sample_id")
            or ""
        ).strip()

        text = (
            row.get("caption")
            or ""
        ).strip()

        caption = text

        comments = (
            row.get("comments")
            or ""
        ).strip()

        reference_label = (
            row.get(
                "provisional_label"
            )
            or ""
        ).strip().upper()

        print(
            f"[{index:02}/{len(dataset):02}] "
            f"{sample_id} ...",
            end=" ",
            flush=True
        )

        try:

            response, latency = (
                call_guardnet(
                    text=text,
                    caption=caption,
                    comments=comments
                )
            )

            prediction = extract_prediction(
                response
            )

            latencies.append(
                latency
            )

            results.append({
                "sample_id":
                    sample_id,

                "provisional_label":
                    reference_label,

                "predicted_label":
                    prediction[
                        "label"
                    ],

                "confidence":
                    round(
                        prediction[
                            "confidence"
                        ],
                        6
                    ),

                "risk_score":
                    round(
                        prediction[
                            "risk_score"
                        ],
                        6
                    ),

                "latency_ms":
                    round(
                        latency,
                        3
                    ),

                "status":
                    prediction[
                        "status"
                    ],
            })

            print(
                f"{prediction['label']} "
                f"({prediction['confidence']:.4f}) "
                f"{latency:.2f} ms"
            )

        except Exception as e:

            print(
                "ERROR"
            )

            errors.append({
                "sample_id":
                    sample_id,

                "error":
                    str(e)
            })

            results.append({
                "sample_id":
                    sample_id,

                "provisional_label":
                    reference_label,

                "predicted_label":
                    "ERROR",

                "confidence":
                    0.0,

                "risk_score":
                    0.0,

                "latency_ms":
                    0.0,

                "status":
                    "error",
            })

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    y_true = [
        row[
            "provisional_label"
        ]
        for row in results
        if (
            row[
                "provisional_label"
            ]
            in VALID_LABELS
            and
            row[
                "predicted_label"
            ]
            in VALID_LABELS
        )
    ]

    y_pred = [
        row[
            "predicted_label"
        ]
        for row in results
        if (
            row[
                "provisional_label"
            ]
            in VALID_LABELS
            and
            row[
                "predicted_label"
            ]
            in VALID_LABELS
        )
    ]

    metrics = calculate_metrics(
        y_true,
        y_pred
    )

    matrix = confusion_matrix(
        y_true,
        y_pred
    )

    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_id",
                "provisional_label",
                "predicted_label",
                "confidence",
                "risk_score",
                "latency_ms",
                "status",
            ]
        )

        writer.writeheader()

        writer.writerows(
            results
        )

    write_report(
        results,
        metrics,
        latencies,
        errors,
        matrix
    )

    print()
    print("=" * 72)
    print(
        "PILOT RESULTS"
    )
    print("=" * 72)

    if metrics[
        "accuracy"
    ] is not None:

        print(
            f"Accuracy      : "
            f"{metrics['accuracy'] * 100:.2f}%"
        )

        print(
            f"Macro Precision: "
            f"{metrics['macro_precision']:.4f}"
        )

        print(
            f"Macro Recall   : "
            f"{metrics['macro_recall']:.4f}"
        )

        print(
            f"Macro F1       : "
            f"{metrics['macro_f1']:.4f}"
        )

        print(
            f"F1 C2          : "
            f"{metrics['f1_c2']:.4f}"
        )

    else:

        print(
            "Metrics tidak dapat dihitung."
        )

    if latencies:

        print(
            f"Mean latency   : "
            f"{statistics.mean(latencies):.2f} ms"
        )

        print(
            f"Median latency : "
            f"{statistics.median(latencies):.2f} ms"
        )

    print()

    print(
        "CSV saved:"
    )

    print(
        RESULT_FILE
    )

    print()

    print(
        "Report saved:"
    )

    print(
        REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Hasil ini adalah PILOT/PRELIMINARY."
    )

    print(
        "Jangan masukkan sebagai final model performance "
        "sebelum final ground truth tersedia."
    )

    print()


if __name__ == "__main__":
    main()