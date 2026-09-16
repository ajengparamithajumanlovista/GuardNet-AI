# GuardNet-AI — Final Human Annotation System

## 1. Put these files in the backend/research folder

```text
backend/
└── research/
    ├── annotation_app.py
    ├── merge_annotations.py
    ├── dataset_master.csv
    └── annotations/
```

The app creates `annotations/` automatically.

## 2. Annotator 1

From:

```powershell
cd "D:\GEMASTIK\GuardNet-AI_RESEARCH_PUBLICATION_EDITION\backend\research"
```

run:

```powershell
python .\annotation_app.py --annotator A1
```

Open:

```text
http://127.0.0.1:8765
```

## 3. Annotator 2

STOP the A1 server with Ctrl+C first.

Then:

```powershell
python .\annotation_app.py --annotator A2
```

Open the same browser address.

The outputs are separated:

```text
annotations/A1_annotations.csv
annotations/A2_annotations.csv
```

## 4. IMPORTANT INDEPENDENCE RULE

A1 and A2 must NOT look at each other's labels.
They must NOT use GuardNet-AI predictions as their labels.

## 5. After both annotators finish

Run:

```powershell
python .\merge_annotations.py
```

The program creates:

```text
final_ground_truth.csv
annotation_quality_report.txt
```

If there are disagreements, `final_label` remains empty and the report says adjudication is required.

Do NOT manually fill the final label based on the model prediction.

## 6. Pilot dataset vs final dataset

The current 15 rows are only pilot/test data.
They must not be reported as the final 3,000-unit research dataset.

Before final KTI claims, replace/expand `dataset_master.csv` with the actual collected dataset following the research protocol.

## 7. Research integrity

The software calculates metrics from actual entered data. It does not invent:
- Cohen's Kappa
- class distribution
- agreement
- final labels
- model performance

If data are incomplete, the software reports them as incomplete.
