import cv2
import numpy as np


# ============================================================
# GuardNet-AI
# VISUAL INTELLIGENCE ENGINE
# ============================================================
#
# Purpose:
#   Extract visual evidence from Instagram images.
#
# Features:
#   - brightness
#   - contrast
#   - saturation
#   - colorfulness
#   - edge density
#   - visual text density
#   - high-saturation ratio
#   - promotional visual score
#
# IMPORTANT:
#   This module is a visual feature/evidence analyzer.
#   It is NOT a deep-learning image classifier.
#
# Backward compatible:
#   visual_score
# ============================================================


# ============================================================
# SAFE NORMALIZATION
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):
    return max(
        minimum,
        min(
            float(value),
            maximum
        )
    )


# ============================================================
# ANALYZE IMAGE
# ============================================================

def analyze_image(
    image
):
    """
    Analyze visual characteristics of an image.

    Returns:
        width
        height
        brightness
        contrast
        saturation
        colorfulness
        edge_density
        text_density
        high_saturation_ratio
        visual_score
        evidence
        status
    """

    try:

        # ----------------------------------------------------
        # Validate image
        # ----------------------------------------------------

        if image is None:

            return {
                "visual_score": 0.0,
                "status": "empty",
                "evidence": []
            }


        # ----------------------------------------------------
        # PIL -> RGB
        # ----------------------------------------------------

        img = image.convert(
            "RGB"
        )


        # ----------------------------------------------------
        # PIL -> numpy
        # ----------------------------------------------------

        rgb = np.array(
            img
        )


        # ----------------------------------------------------
        # Basic dimensions
        # ----------------------------------------------------

        width, height = img.size


        if width <= 0 or height <= 0:

            return {
                "visual_score": 0.0,
                "status": "invalid_image",
                "evidence": []
            }


        # ----------------------------------------------------
        # RGB -> OpenCV BGR
        # ----------------------------------------------------

        bgr = cv2.cvtColor(
            rgb,
            cv2.COLOR_RGB2BGR
        )


        # ----------------------------------------------------
        # Grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2GRAY
        )


        # ----------------------------------------------------
        # HSV
        # ----------------------------------------------------

        hsv = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2HSV
        )


        # ====================================================
        # 1. BRIGHTNESS
        # ====================================================

        brightness = float(
            np.mean(gray)
        )


        brightness_normalized = (
            brightness / 255.0
        )


        # ====================================================
        # 2. CONTRAST
        # ====================================================

        contrast = float(
            np.std(gray)
        )


        contrast_normalized = clamp(
            contrast / 80.0
        )


        # ====================================================
        # 3. SATURATION
        # ====================================================

        saturation = float(
            np.mean(
                hsv[:, :, 1]
            )
        )


        saturation_normalized = (
            saturation / 255.0
        )


        # ====================================================
        # 4. HIGH SATURATION RATIO
        # ====================================================

        high_saturation_mask = (
            hsv[:, :, 1] > 180
        )


        high_saturation_ratio = float(
            np.mean(
                high_saturation_mask
            )
        )


        # ====================================================
        # 5. COLORFULNESS
        # ====================================================
        #
        # Approximation using channel dispersion.
        # ====================================================

        r = rgb[:, :, 0].astype(
            np.float32
        )

        g = rgb[:, :, 1].astype(
            np.float32
        )

        b = rgb[:, :, 2].astype(
            np.float32
        )


        rg = np.abs(
            r - g
        )

        yb = np.abs(
            (
                0.5 * (r + g)
            ) - b
        )


        colorfulness = float(
            np.sqrt(
                np.mean(
                    rg ** 2
                )
                +
                np.mean(
                    yb ** 2
                )
            )
        )


        colorfulness_normalized = clamp(
            colorfulness / 100.0
        )


        # ====================================================
        # 6. EDGE DENSITY
        # ====================================================

        edges = cv2.Canny(
            gray,
            100,
            200
        )


        edge_density = float(
            np.mean(
                edges > 0
            )
        )


        edge_density_normalized = clamp(
            edge_density * 5.0
        )


        # ====================================================
        # 7. TEXT-LIKE DENSITY
        # ====================================================
        #
        # Approximation based on edges and local structure.
        #
        # This does NOT replace OCR.
        # ====================================================

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3)
        )


        morphed = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel
        )


        text_like_density = float(
            np.mean(
                morphed > 0
            )
        )


        text_density = clamp(
            text_like_density * 4.0
        )


        # ====================================================
        # 8. VISUAL CHARACTERISTICS
        # ====================================================

        evidence = []


        # Bright promotional design
        if brightness_normalized > 0.70:

            evidence.append(
                "bright_visual"
            )


        # High saturation
        if saturation_normalized > 0.60:

            evidence.append(
                "high_saturation"
            )


        # Strong colorfulness
        if colorfulness_normalized > 0.55:

            evidence.append(
                "high_colorfulness"
            )


        # Dense visual elements
        if edge_density_normalized > 0.35:

            evidence.append(
                "dense_visual_elements"
            )


        # Text-heavy visual
        if text_density > 0.35:

            evidence.append(
                "text_heavy_visual"
            )


        # High contrast
        if contrast_normalized > 0.60:

            evidence.append(
                "high_contrast"
            )


        # ====================================================
        # 9. PROMOTIONAL VISUAL SCORE
        # ====================================================
        #
        # These are visual characteristics, NOT proof of gambling.
        # ====================================================

        visual_score = (

            brightness_normalized * 0.15

            +

            contrast_normalized * 0.15

            +

            saturation_normalized * 0.20

            +

            colorfulness_normalized * 0.20

            +

            edge_density_normalized * 0.10

            +

            text_density * 0.20

        )


        visual_score = clamp(
            visual_score
        )


        # ====================================================
        # 10. RETURN
        # ====================================================

        return {

            "width":
                width,

            "height":
                height,

            "brightness":
                round(
                    brightness,
                    3
                ),

            "contrast":
                round(
                    contrast,
                    3
                ),

            "saturation":
                round(
                    saturation,
                    3
                ),

            "colorfulness":
                round(
                    colorfulness,
                    3
                ),

            "edge_density":
                round(
                    edge_density,
                    4
                ),

            "text_density":
                round(
                    text_density,
                    4
                ),

            "high_saturation_ratio":
                round(
                    high_saturation_ratio,
                    4
                ),

            "visual_score":
                round(
                    visual_score,
                    3
                ),

            "evidence":
                evidence,

            "status":
                "success"

        }


    except Exception as e:

        return {

            "visual_score":
                0.0,

            "evidence":
                [],

            "status":
                "failed",

            "error":
                str(e)

        }