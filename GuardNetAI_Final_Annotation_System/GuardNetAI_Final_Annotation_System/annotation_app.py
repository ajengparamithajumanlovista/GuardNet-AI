# ============================================================
# GUARDNET-AI FINAL ANNOTATION APP
# Standard-library only: no Streamlit / Flask required.
#
# Run:
#   python annotation_app.py --annotator A1
#   python annotation_app.py --annotator A2
#
# Open:
#   http://127.0.0.1:8765
#
# IMPORTANT:
# - A1 and A2 must annotate independently.
# - The app never uses GuardNet-AI predictions as ground truth.
# - It stores each annotator in a separate CSV.
# ============================================================

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset_master.csv"
ANNOTATION_DIR = ROOT / "annotations"
ANNOTATION_DIR.mkdir(exist_ok=True)

PORT = 8765
LABELS = ("C0", "C1", "C2")

LABEL_NAMES = {
    "C0": "Non-Gambling",
    "C1": "Gambling-Related Non-Promotion",
    "C2": "Gambling Promotion",
}

parser = argparse.ArgumentParser()
parser.add_argument("--annotator", required=True, choices=("A1", "A2"))
parser.add_argument("--port", type=int, default=PORT)
args = parser.parse_args()

ANNOTATOR = args.annotator
PORT = args.port
OUTPUT = ANNOTATION_DIR / f"{ANNOTATOR}_annotations.csv"


def read_dataset():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATASET}")

    with DATASET.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("Dataset kosong.")

    return rows


def load_existing():
    if not OUTPUT.exists():
        return {}

    with OUTPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return {
            row["sample_id"]: row
            for row in csv.DictReader(f)
            if row.get("sample_id")
        }


rows = read_dataset()
existing = load_existing()
lock = threading.Lock()


def save_annotation(sample_id, label, notes):
    if label not in LABELS:
        raise ValueError("Label harus C0, C1, atau C2.")

    found = None
    for row in rows:
        if row.get("sample_id") == sample_id:
            found = row
            break

    if found is None:
        raise ValueError("sample_id tidak ditemukan.")

    existing[sample_id] = {
        "sample_id": sample_id,
        "label": label,
        "notes": notes.strip(),
    }

    with lock:
        with OUTPUT.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["sample_id", "label", "notes"],
            )
            writer.writeheader()

            for row in rows:
                sid = row.get("sample_id")
                if sid in existing:
                    writer.writerow(existing[sid])


def page():
    completed = sum(1 for r in rows if r.get("sample_id") in existing)
    total = len(rows)

    next_row = None
    for row in rows:
        if row.get("sample_id") not in existing:
            next_row = row
            break

    if next_row is None:
        body = """
        <div class="done">
          <h2>Semua content unit sudah dianotasi.</h2>
          <p>Jangan mengubah hasil anotasi untuk menyesuaikan prediksi model.</p>
          <p>File anotasi tersimpan di:</p>
          <code>annotations/ANNOTATOR_annotations.csv</code>
        </div>
        """
    else:
        sid = html.escape(next_row.get("sample_id", ""))
        caption = html.escape(next_row.get("caption", ""))
        comments = html.escape(next_row.get("comments", ""))
        source = html.escape(next_row.get("source_type", ""))
        ctype = html.escape(next_row.get("content_type", ""))
        account = html.escape(next_row.get("account_id", ""))

        body = f"""
        <div class="meta">
          <b>Sample:</b> {sid}
          &nbsp; | &nbsp;
          <b>Source:</b> {source}
          &nbsp; | &nbsp;
          <b>Type:</b> {ctype}
        </div>

        <div class="content">
          <h3>Caption / Text</h3>
          <div class="box">{caption or "(kosong)"}</div>

          <h3>Comments</h3>
          <div class="box">{comments or "(tidak tersedia)"}</div>

          <h3>Account ID</h3>
          <div class="box">{account or "(tidak tersedia)"}</div>
        </div>

        <form method="POST" action="/save">
          <input type="hidden" name="sample_id" value="{sid}">

          <h3>Pilih satu label</h3>

          <label class="label c0">
            <input type="radio" name="label" value="C0" required>
            <b>C0 — Non-Gambling</b>
            <span>Tidak merupakan promosi perjudian.</span>
          </label>

          <label class="label c1">
            <input type="radio" name="label" value="C1">
            <b>C1 — Gambling-Related Non-Promotion</b>
            <span>Berkaitan dengan perjudian tetapi tidak mempromosikan/mengajak.</span>
          </label>

          <label class="label c2">
            <input type="radio" name="label" value="C2">
            <b>C2 — Gambling Promotion</b>
            <span>Mengandung indikasi promosi, ajakan, akses, pendaftaran, deposit,
            bonus, jackpot, referral, atau fasilitasi perjudian.</span>
          </label>

          <h3>Catatan anotator (opsional)</h3>
          <textarea name="notes" rows="5"
            placeholder="Tuliskan alasan singkat bila diperlukan. Jangan menulis hasil prediksi model."></textarea>

          <button type="submit">SIMPAN & NEXT</button>
        </form>
        """

    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>GuardNet-AI Annotation — {ANNOTATOR}</title>
<style>
body {{
  font-family: Arial, sans-serif;
  max-width: 900px;
  margin: 30px auto;
  padding: 0 20px;
  background: #f5f7fa;
  color: #17202a;
}}
header, .content, form, .done {{
  background: white;
  padding: 24px;
  border-radius: 14px;
  margin-bottom: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08);
}}
h1 {{ margin-top: 0; }}
.meta {{ padding: 14px; background: #eef2f7; border-radius: 10px; }}
.box {{
  white-space: pre-wrap;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #ddd;
  border-radius: 10px;
  min-height: 25px;
}}
.label {{
  display: block;
  padding: 18px;
  margin: 12px 0;
  border: 2px solid #ddd;
  border-radius: 12px;
  cursor: pointer;
}}
.label:hover {{ border-color: #555; }}
.label span {{ display:block; margin: 7px 0 0 25px; color:#555; }}
textarea {{
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #ccc;
}}
button {{
  margin-top: 18px;
  padding: 13px 24px;
  border: 0;
  border-radius: 10px;
  cursor: pointer;
  font-weight: bold;
}}
.progress {{ color:#555; }}
</style>
</head>
<body>
<header>
<h1>GUARDNET-AI</h1>
<p>Independent Human Annotation</p>
<p><b>Annotator: {ANNOTATOR}</b></p>
<p class="progress">Progress: {completed} / {total}</p>
</header>
{body}
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            content = page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/health":
            content = json.dumps({
                "status": "success",
                "annotator": ANNOTATOR,
                "total": len(rows),
                "completed": sum(
                    1 for r in rows
                    if r.get("sample_id") in existing
                ),
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404)

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)

        sample_id = form.get("sample_id", [""])[0]
        label = form.get("label", [""])[0]
        notes = form.get("notes", [""])[0]

        try:
            save_annotation(sample_id, label, notes)
        except Exception as exc:
            message = html.escape(str(exc))
            self.send_response(400)
            content = f"""
            <html><body>
            <h2>Error</h2>
            <pre>{message}</pre>
            <a href="/">Kembali</a>
            </body></html>
            """.encode()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[{ANNOTATOR}] {fmt % args}")


if __name__ == "__main__":
    print("=" * 65)
    print("GUARDNET-AI — INDEPENDENT ANNOTATION SERVER")
    print("=" * 65)
    print(f"Annotator : {ANNOTATOR}")
    print(f"Dataset   : {DATASET}")
    print(f"Output    : {OUTPUT}")
    print(f"Samples   : {len(rows)}")
    print()
    print(f"Open: http://127.0.0.1:{PORT}")
    print()
    print("STOP SERVER: Ctrl+C")
    print("=" * 65)

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
