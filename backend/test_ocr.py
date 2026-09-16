from PIL import Image

from app.ocr.engine import run_ocr


# ============================================================
# GUARDNET-AI OCR TEST
# ============================================================

IMAGE_PATH = r"dataset\instagram\judi1.jpg"


# ============================================================
# HEADER
# ============================================================

print()
print("==============================================")
print(" GUARDNET-AI OCR TEST")
print("==============================================")
print()

print(
    "Image:",
    IMAGE_PATH
)


# ============================================================
# LOAD IMAGE
# ============================================================

try:

    image = Image.open(
        IMAGE_PATH
    ).convert(
        "RGB"
    )

except Exception as error:

    print()
    print("ERROR: Gagal membuka gambar.")
    print()
    print(error)
    print()

    print(
        "Pastikan file berada di:"
    )

    print(
        r"backend\dataset\instagram\judi1.jpg"
    )

    raise SystemExit


# ============================================================
# RUN OCR
# ============================================================

print()
print("Menjalankan OCR...")
print()


result = run_ocr(
    image
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("=== HASIL OCR GUARDNET-AI ===")
print()


print("Text:")
print(
    result.get(
        "text",
        ""
    )
)

print()


print("Normalized Text:")
print(
    result.get(
        "normalized_text",
        ""
    )
)

print()


print("Confidence:")
print(
    result.get(
        "confidence",
        0
    )
)

print()


print("Quality:")
print(
    result.get(
        "quality",
        0
    )
)

print()


print("Gambling Terms:")
print(
    result.get(
        "gambling_terms",
        []
    )
)

print()


print("Promotional Terms:")
print(
    result.get(
        "promotional_terms",
        []
    )
)

print()


print("Preprocessing:")
print(
    result.get(
        "preprocessing"
    )
)

print()


print("Variants Tested:")
print(
    result.get(
        "variants_tested",
        0
    )
)

print()


print("Status:")
print(
    result.get(
        "status"
    )
)

print()


print("==============================================")
print(" OCR TEST SELESAI")
print("==============================================")
print()