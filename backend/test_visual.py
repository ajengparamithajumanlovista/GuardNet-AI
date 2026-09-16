from PIL import Image
from app.vision.model import analyze_image


# ============================================================
# GuardNet-AI
# VISUAL ENGINE TEST
# ============================================================

IMAGE_PATH = "ocr_test.png"


print("=== HASIL VISUAL ANALYSIS GUARDNET-AI ===")


try:

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = Image.open(
        IMAGE_PATH
    )


    # --------------------------------------------------------
    # Analyze image
    # --------------------------------------------------------

    result = analyze_image(
        image
    )


    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print(result)


except Exception as e:

    print({
        "status": "failed",
        "error": str(e)
    })