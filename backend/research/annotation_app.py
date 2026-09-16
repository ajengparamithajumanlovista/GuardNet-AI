# ============================================================
# GUARDNET-AI
# FINAL HUMAN ANNOTATION APPLICATION
# FOR RESEARCH / KARYA TULIS ILMIAH
#
# Version: Research Final
#
# IMPORTANT RESEARCH RULE:
# - Annotator 1 and Annotator 2 work independently.
# - Model prediction is NOT shown to annotators.
# - Model prediction is NOT used as ground truth.
# - Each annotator has a separate output file.
# - Final ground truth is produced only after agreement/
#   adjudication.
# ============================================================

from __future__ import annotations

import argparse
import csv
import html
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent

DATASET_FILE = ROOT / "dataset_master.csv"

ANNOTATION_DIR = ROOT / "annotations"

ANNOTATION_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# LABEL CONFIGURATION
# ============================================================

VALID_LABELS = (
    "C0",
    "C1",
    "C2"
)


LABEL_NAMES = {

    "C0":
        "Non-Gambling",

    "C1":
        "Gambling-Related Non-Promotion",

    "C2":
        "Gambling Promotion"

}


LABEL_DESCRIPTIONS = {

    "C0":
        (
            "Konten tidak mempromosikan perjudian "
            "dan tidak memiliki tujuan promosi perjudian."
        ),

    "C1":
        (
            "Konten berkaitan dengan perjudian tetapi "
            "tidak menunjukkan tujuan promosi atau ajakan."
        ),

    "C2":
        (
            "Konten menunjukkan tujuan promosi, ajakan, "
            "pendaftaran, deposit, bonus, jackpot, referral, "
            "link akses, atau fasilitasi perjudian."
        )

}


# ============================================================
# COMMAND LINE
# ============================================================

parser = argparse.ArgumentParser(

    description=
        "GuardNet-AI Independent Human Annotation System"

)


parser.add_argument(

    "--annotator",

    required=True,

    choices=[
        "A1",
        "A2"
    ],

    help=
        "Identifier anotator: A1 atau A2"

)


parser.add_argument(

    "--port",

    type=int,

    default=8765,

    help=
        "Port server lokal"

)


args = parser.parse_args()


ANNOTATOR = args.annotator

PORT = args.port


# ============================================================
# OUTPUT FILE
# ============================================================

OUTPUT_FILE = (

    ANNOTATION_DIR
    /
    f"{ANNOTATOR}_annotations.csv"

)


# ============================================================
# DATASET LOADER
# ============================================================

def load_dataset():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(

            "Dataset tidak ditemukan:\n\n"

            f"{DATASET_FILE}\n\n"

            "Pastikan dataset_master.csv berada "
            "di folder research."

        )


    with open(

        DATASET_FILE,

        "r",

        encoding="utf-8-sig",

        newline=""

    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)


    if not rows:

        raise ValueError(

            "Dataset kosong."

        )


    required_columns = {

        "sample_id",

        "source_type",

        "content_type",

        "caption",

        "comments",

        "account_id"

    }


    actual_columns = set(

        reader.fieldnames or []

    )


    missing = (

        required_columns
        -
        actual_columns

    )


    if missing:

        raise ValueError(

            "Kolom dataset tidak lengkap.\n"

            "Kolom yang hilang:\n"

            +
            "\n".join(
                sorted(missing)
            )

        )


    return rows


# ============================================================
# EXISTING ANNOTATIONS
# ============================================================

def load_annotations():

    if not OUTPUT_FILE.exists():

        return {}


    with open(

        OUTPUT_FILE,

        "r",

        encoding="utf-8-sig",

        newline=""

    ) as file:

        reader = csv.DictReader(file)


        result = {}


        for row in reader:

            sample_id = (

                row
                .get(
                    "sample_id",
                    ""
                )
                .strip()

            )


            if sample_id:

                result[
                    sample_id
                ] = {

                    "label":
                        row.get(
                            "label",
                            ""
                        ).strip(),

                    "notes":
                        row.get(
                            "notes",
                            ""
                        ).strip()

                }


        return result


# ============================================================
# INITIALIZE
# ============================================================

rows = load_dataset()

annotations = load_annotations()

lock = threading.Lock()


# ============================================================
# SAVE ANNOTATION
# ============================================================

def save_annotation(

    sample_id,

    label,

    notes

):

    sample_id = (

        sample_id
        .strip()

    )


    label = (

        label
        .strip()
        .upper()

    )


    notes = (

        notes
        .strip()

    )


    if label not in VALID_LABELS:

        raise ValueError(

            "Label tidak valid. "
            "Gunakan C0, C1, atau C2."

        )


    valid_sample = any(

        row.get(
            "sample_id",
            ""
        ).strip()
        ==
        sample_id

        for row in rows

    )


    if not valid_sample:

        raise ValueError(

            "sample_id tidak ditemukan."

        )


    annotations[
        sample_id
    ] = {

        "label":
            label,

        "notes":
            notes

    }


    # --------------------------------------------------------
    # WRITE CSV
    # --------------------------------------------------------

    with lock:

        with open(

            OUTPUT_FILE,

            "w",

            encoding="utf-8",

            newline=""

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=[

                    "sample_id",

                    "label",

                    "notes"

                ]

            )


            writer.writeheader()


            for row in rows:

                sid = (

                    row
                    .get(
                        "sample_id",
                        ""
                    )
                    .strip()

                )


                if sid in annotations:

                    writer.writerow({

                        "sample_id":
                            sid,

                        "label":
                            annotations[
                                sid
                            ][
                                "label"
                            ],

                        "notes":
                            annotations[
                                sid
                            ][
                                "notes"
                            ]

                    })


# ============================================================
# PROGRESS
# ============================================================

def get_progress():

    completed = len(

        annotations

    )


    total = len(

        rows

    )


    return completed, total


# ============================================================
# NEXT SAMPLE
# ============================================================

def get_next_sample():

    for row in rows:

        sample_id = (

            row
            .get(
                "sample_id",
                ""
            )
            .strip()

        )


        if sample_id not in annotations:

            return row


    return None


# ============================================================
# HTML PAGE
# ============================================================

def render_page():

    completed, total = (

        get_progress()

    )


    sample = get_next_sample()


    # --------------------------------------------------------
    # ALL DONE
    # --------------------------------------------------------

    if sample is None:

        body = """

        <div class="card done">

            <h2>
                Semua content unit telah dianotasi.
            </h2>

            <p>
                Tidak ada sample yang tersisa.
            </p>

            <p>
                File hasil anotasi:
            </p>

            <pre>
annotations/
            </pre>

            <p>
                Jangan mengubah label berdasarkan
                prediksi GuardNet-AI.
            </p>

        </div>

        """


    else:

        sample_id = html.escape(

            sample.get(
                "sample_id",
                ""
            )

        )


        source_type = html.escape(

            sample.get(
                "source_type",
                ""
            )

        )


        content_type = html.escape(

            sample.get(
                "content_type",
                ""
            )

        )


        account_id = html.escape(

            sample.get(
                "account_id",
                ""
            )

        )


        caption = html.escape(

            sample.get(
                "caption",
                ""
            )

        )


        comments = html.escape(

            sample.get(
                "comments",
                ""
            )

        )


        body = f"""

        <div class="card">

            <div class="metadata">

                <div>
                    <b>Sample ID:</b>
                    {sample_id}
                </div>

                <div>
                    <b>Source:</b>
                    {source_type}
                </div>

                <div>
                    <b>Content Type:</b>
                    {content_type}
                </div>

                <div>
                    <b>Account ID:</b>
                    {account_id}
                </div>

            </div>


            <h2>
                Content
            </h2>


            <h3>
                Caption / Text
            </h3>

            <div class="content-box">

                {
                    caption
                    if caption
                    else
                    "(Caption kosong)"
                }

            </div>


            <h3>
                Comments
            </h3>

            <div class="content-box">

                {
                    comments
                    if comments
                    else
                    "(Komentar tidak tersedia)"
                }

            </div>


            <hr>


            <h2>
                Pilih Label
            </h2>


            <form
                method="POST"
                action="/save"
            >

                <input
                    type="hidden"
                    name="sample_id"
                    value="{sample_id}"
                >


                <label class="option">

                    <input
                        type="radio"
                        name="label"
                        value="C0"
                        required
                    >

                    <span>

                        <b>
                            C0 — Non-Gambling
                        </b>

                        <small>

                            {LABEL_DESCRIPTIONS["C0"]}

                        </small>

                    </span>

                </label>


                <label class="option">

                    <input
                        type="radio"
                        name="label"
                        value="C1"
                    >

                    <span>

                        <b>
                            C1 — Gambling-Related Non-Promotion
                        </b>

                        <small>

                            {LABEL_DESCRIPTIONS["C1"]}

                        </small>

                    </span>

                </label>


                <label class="option">

                    <input
                        type="radio"
                        name="label"
                        value="C2"
                    >

                    <span>

                        <b>
                            C2 — Gambling Promotion
                        </b>

                        <small>

                            {LABEL_DESCRIPTIONS["C2"]}

                        </small>

                    </span>

                </label>


                <h3>
                    Catatan
                </h3>


                <textarea

                    name="notes"

                    placeholder=
                        "Tuliskan alasan singkat jika diperlukan."

                    rows="5"

                ></textarea>


                <button
                    type="submit"
                >

                    SIMPAN & NEXT

                </button>


            </form>

        </div>

        """


    return f"""

<!DOCTYPE html>

<html lang="id">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>
GuardNet-AI Annotation
</title>


<style>

* {{
    box-sizing: border-box;
}}


body {{

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #f4f6f8;

    color:
        #17202a;

}}


.container {{

    max-width:
        900px;

    margin:
        30px auto;

    padding:
        0 20px;

}}


.header {{

    background:
        #111827;

    color:
        white;

    padding:
        25px;

    border-radius:
        14px;

    margin-bottom:
        20px;

}}


.header h1 {{

    margin:
        0 0 8px 0;

}}


.progress {{

    margin-top:
        15px;

    background:
        #374151;

    border-radius:
        10px;

    overflow:
        hidden;

    height:
        12px;

}}


.progress-bar {{

    height:
        100%;

    width:
        {
            (
                completed
                /
                total
                *
                100
            )
            if total
            else
            0
        }%;

    background:
        #10b981;

}}


.card {{

    background:
        white;

    padding:
        25px;

    border-radius:
        14px;

    margin-bottom:
        20px;

    box-shadow:
        0 2px 12px
        rgba(
            0,
            0,
            0,
            .08
        );

}}


.metadata {{

    display:
        grid;

    grid-template-columns:
        repeat(
            2,
            1fr
        );

    gap:
        10px;

    padding:
        15px;

    background:
        #f3f4f6;

    border-radius:
        10px;

}}


.content-box {{

    white-space:
        pre-wrap;

    border:
        1px solid #d1d5db;

    background:
        #fafafa;

    border-radius:
        10px;

    padding:
        16px;

    min-height:
        50px;

    line-height:
        1.6;

}}


.option {{

    display:
        flex;

    gap:
        14px;

    align-items:
        flex-start;

    padding:
        18px;

    margin:
        12px 0;

    border:
        2px solid #d1d5db;

    border-radius:
        12px;

    cursor:
        pointer;

}}


.option:hover {{

    border-color:
        #111827;

}}


.option input {{

    margin-top:
        4px;

    transform:
        scale(1.3);

}}


.option small {{

    display:
        block;

    margin-top:
        7px;

    color:
        #4b5563;

    line-height:
        1.5;

}}


textarea {{

    width:
        100%;

    padding:
        12px;

    border:
        1px solid #d1d5db;

    border-radius:
        10px;

    resize:
        vertical;

    font-family:
        inherit;

}}


button {{

    width:
        100%;

    padding:
        15px;

    margin-top:
        20px;

    border:
        none;

    border-radius:
        10px;

    background:
        #111827;

    color:
        white;

    font-size:
        16px;

    font-weight:
        bold;

    cursor:
        pointer;

}}


button:hover {{

    opacity:
        .9;

}}


.done {{

    text-align:
        center;

}}


code,
pre {{

    background:
        #f3f4f6;

    padding:
        10px;

    border-radius:
        8px;

}}


@media(
    max-width:700px
) {{

    .metadata {{

        grid-template-columns:
            1fr;

    }}

}}

</style>

</head>


<body>


<div class="container">


<div class="header">

<h1>
GUARDNET-AI
</h1>

<div>
Independent Human Annotation System
</div>

<div style="margin-top:10px">

<b>
Annotator:
{ANNOTATOR}
</b>

</div>

<div style="margin-top:10px">

Progress:
<b>
{completed}
/
{total}
</b>

</div>


<div class="progress">

<div class="progress-bar"></div>

</div>

</div>


{body}


</div>


</body>

</html>

"""


# ============================================================
# HTTP SERVER
# ============================================================

class AnnotationHandler(
    BaseHTTPRequestHandler
):


    def do_GET(self):

        if self.path == "/":

            content = (

                render_page()
                .encode(
                    "utf-8"
                )

            )


            self.send_response(
                200
            )


            self.send_header(

                "Content-Type",

                "text/html; charset=utf-8"

            )


            self.send_header(

                "Content-Length",

                str(
                    len(content)
                )

            )


            self.end_headers()


            self.wfile.write(
                content
            )


            return


        if self.path == "/health":

            completed, total = (

                get_progress()

            )


            content = (

                f"""

                {{
                    "status": "success",
                    "annotator": "{ANNOTATOR}",
                    "completed": {completed},
                    "total": {total}
                }}

                """
                .encode(
                    "utf-8"
                )

            )


            self.send_response(
                200
            )


            self.send_header(

                "Content-Type",

                "application/json"

            )


            self.send_header(

                "Content-Length",

                str(
                    len(content)
                )

            )


            self.end_headers()


            self.wfile.write(
                content
            )


            return


        self.send_error(
            404
        )


    def do_POST(self):

        if self.path != "/save":

            self.send_error(
                404
            )

            return


        try:

            length = int(

                self.headers.get(
                    "Content-Length",
                    "0"
                )

            )


            raw_data = (

                self.rfile
                .read(length)
                .decode(
                    "utf-8"
                )

            )


            form = parse_qs(
                raw_data
            )


            sample_id = (

                form
                .get(
                    "sample_id",
                    [""]
                )[0]

            )


            label = (

                form
                .get(
                    "label",
                    [""]
                )[0]

            )


            notes = (

                form
                .get(
                    "notes",
                    [""]
                )[0]

            )


            save_annotation(

                sample_id,

                label,

                notes

            )


            self.send_response(
                303
            )


            self.send_header(

                "Location",
                "/"

            )


            self.end_headers()


        except Exception as error:

            message = html.escape(
                str(error)
            )


            content = f"""

            <!DOCTYPE html>

            <html>

            <body>

            <h2>
                Terjadi kesalahan
            </h2>

            <pre>
                {message}
            </pre>

            <a href="/">
                Kembali
            </a>

            </body>

            </html>

            """.encode(
                "utf-8"
            )


            self.send_response(
                400
            )


            self.send_header(

                "Content-Type",

                "text/html; charset=utf-8"

            )


            self.send_header(

                "Content-Length",

                str(
                    len(content)
                )

            )


            self.end_headers()


            self.wfile.write(
                content
            )


    def log_message(

        self,

        format,

        *args

    ):

        print(

            f"[GuardNet-AI {ANNOTATOR}] "
            +
            (
                format
                %
                args
            )

        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print(
        "=" * 65
    )

    print(
        " GUARDNET-AI — FINAL HUMAN ANNOTATION"
    )

    print(
        "=" * 65
    )

    print()

    print(
        f"Annotator : {ANNOTATOR}"
    )

    print(
        f"Dataset   : {DATASET_FILE}"
    )

    print(
        f"Output    : {OUTPUT_FILE}"
    )

    print(
        f"Samples   : {len(rows)}"
    )

    print()

    print(
        f"Open browser:"
    )

    print(
        f"http://127.0.0.1:{PORT}"
    )

    print()

    print(
        "Tekan CTRL+C untuk menghentikan server."
    )

    print()

    print(
        "=" * 65
    )


    server = ThreadingHTTPServer(

        (
            "127.0.0.1",
            PORT
        ),

        AnnotationHandler

    )


    try:

        server.serve_forever()


    except KeyboardInterrupt:

        print()

        print(
            "Annotation server dihentikan."
        )


    finally:

        server.server_close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()