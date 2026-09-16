from PIL import Image
import pytesseract
import cv2
import numpy as np


# lokasi executable Tesseract Windows
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def run_ocr(image):

    """
    OCR Engine GuardNet-AI

    Preprocessing:
    - grayscale
    - resize
    - threshold
    """

    # Convert PIL image ke numpy
    img = np.array(image)


    # grayscale
    gray = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2GRAY
    )


    # resize agar teks kecil terbaca
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2
    )


    # threshold
    _, thresh = cv2.threshold(
        gray,
        150,
        255,
        cv2.THRESH_BINARY
    )


    # OCR
    text = pytesseract.image_to_string(
        thresh,
        lang="eng"
    )


    return {

        "text": text.strip(),

        "length": len(text),

        "status": "success"
    }