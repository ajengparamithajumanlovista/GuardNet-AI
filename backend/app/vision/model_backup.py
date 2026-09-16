from PIL import Image
import numpy as np


def analyze_image(image):

    try:
        # Pastikan RGB
        img = image.convert("RGB")

        # ubah menjadi array
        arr = np.array(img)

        # ukuran gambar
        width, height = img.size

        # rata-rata warna
        mean_rgb = arr.mean(axis=(0, 1))

        # tingkat kecerahan
        brightness = float(arr.mean())


        # deteksi sederhana karakteristik visual
        visual_score = 0.5


        # indikator gambar promosi mencolok
        if brightness > 180:
            visual_score += 0.1


        return {
            "width": width,
            "height": height,

            "brightness": brightness,

            "mean_rgb": {
                "r": float(mean_rgb[0]),
                "g": float(mean_rgb[1]),
                "b": float(mean_rgb[2])
            },

            "visual_score": min(
                visual_score,
                1.0
            )
        }


    except Exception as e:

        return {
            "visual_score":0,
            "error":str(e)
        }