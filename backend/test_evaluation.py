import csv
from collections import Counter

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# GUARDNET-AI
# CLASSIFICATION EVALUATION
# ============================================================

DATASET_FILE = "evaluation_dataset.csv"

LABELS = [
    "C0",
    "C1",
    "C2"
]


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    rows = []

    try:

        with open(
            DATASET_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                text = (
                    row.get(
                        "text",
                        ""
                    )
                    or ""
                ).strip()

                true_label = (
                    row.get(
                        "true_label",
                        ""
                    )
                    or ""
                ).strip().upper()


                if not text:
                    continue

                if true_label not in LABELS:
                    continue


                rows.append({

                    "text": text,

                    "true_label":
                        true_label

                })


    except FileNotFoundError:

        print(
            "\nERROR: evaluation_dataset.csv "
            "tidak ditemukan.\n"
        )

        return []


    return rows


# ============================================================
# IMPORT CLASSIFIER
# ============================================================

try:

    from app.models.classifier import (
        classify_text
    )

except Exception as e:

    print(
        "\nERROR: gagal mengimport classifier."
    )

    print(e)

    raise


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print()
    print("=" * 50)
    print(" GUARDNET-AI CLASSIFICATION EVALUATION")
    print("=" * 50)
    print()


    dataset = load_dataset()


    if not dataset:

        print(
            "ERROR: Dataset kosong."
        )

        return


    print(
        "Total data:",
        len(dataset)
    )

    print()


    y_true = []
    y_pred = []


    # ========================================================
    # PREDICTION
    # ========================================================

    for index, row in enumerate(
        dataset,
        start=1
    ):

        text = row["text"]

        true_label = row[
            "true_label"
        ]


        result = classify_text(
            text
        )


        predicted_label = result.get(
            "label",
            "C0"
        )


        y_true.append(
            true_label
        )

        y_pred.append(
            predicted_label
        )


        print(
            f"{index}. "
            f"TRUE={true_label} "
            f"PRED={predicted_label}"
        )


    # ========================================================
    # METRICS
    # ========================================================

    accuracy = accuracy_score(
        y_true,
        y_pred
    )


    precision = precision_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )


    recall = recall_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )


    f1 = f1_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0
    )


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS
    )


    # ========================================================
    # REPORT
    # ========================================================

    report = classification_report(

        y_true,

        y_pred,

        labels=LABELS,

        target_names=LABELS,

        zero_division=0

    )


    # ========================================================
    # COUNTS
    # ========================================================

    ground_truth_count = Counter(
        y_true
    )

    prediction_count = Counter(
        y_pred
    )


    # ========================================================
    # OUTPUT
    # ========================================================

    print()

    print(
        "Accuracy  : "
        f"{accuracy:.4f}"
    )

    print(
        "Precision : "
        f"{precision:.4f}"
    )

    print(
        "Recall    : "
        f"{recall:.4f}"
    )

    print(
        "F1-Score  : "
        f"{f1:.4f}"
    )


    print()

    print(
        "Labels:",
        LABELS
    )


    print()

    print(
        "Confusion Matrix:"
    )

    print(
        matrix
    )


    print()

    print(
        report
    )


    print(
        "Ground Truth:",
        dict(
            sorted(
                ground_truth_count.items()
            )
        )
    )


    print(
        "Prediction:",
        dict(
            sorted(
                prediction_count.items()
            )
        )
    )


    print()

    print("=" * 50)
    print(
        " EVALUATION SELESAI"
    )
    print("=" * 50)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()