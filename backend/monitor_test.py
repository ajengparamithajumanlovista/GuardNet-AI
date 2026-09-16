import requests
import os


print(
    "🚀 GuardNet-AI Instagram Monitoring Started"
)


# ==========================================
# SIMULASI INSTAGRAM POST
# ==========================================

caption = """
Slot gacor bonus besar deposit QRIS daftar sekarang
"""


# ==========================================
# IMAGE PATH HANDLING
# ==========================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            CURRENT_DIR
        )
    )
)


image_path = os.path.join(
    BASE_DIR,
    "dataset",
    "instagram",
    "judi1.jpg.jpeg"
)



print("\n====================")
print("New Instagram Post Detected")
print("====================")


print("\nCaption:")
print(caption)


print("\nImage:")
print(image_path)



# ==========================================
# SEND TO GUARDNET-AI BACKEND
# ==========================================


API_URL = (
    "http://127.0.0.1:8000/analyze-image"
)



try:


    with open(
        image_path,
        "rb"
    ) as image_file:


        files = {

            "image":
                image_file

        }


        data = {

            "caption":
                caption

        }



        response = requests.post(

            API_URL,

            files=files,

            data=data,

            timeout=60

        )



    # ======================================
    # CHECK RESPONSE
    # ======================================


    if response.status_code != 200:


        print(
            "\n❌ Backend Error:",
            response.status_code
        )


        print(
            response.text
        )


        exit()



    result = response.json()



    print("\n====================")
    print("GuardNet-AI Result")
    print("====================")


    print(result)



    # ======================================
    # THREAT CLASSIFICATION
    # ======================================


    classification = (

        result
        .get(
            "classification",
            {}
        )
        .get(
            "classification",
            "C0"
        )

    )



    risk_score = (

        result
        .get(
            "classification",
            {}
        )
        .get(
            "risk_score",
            0
        )

    )



    print(
        "\nClassification:",
        classification
    )


    print(
        "Risk Score:",
        risk_score
    )



    # ======================================
    # ALERT SYSTEM
    # ======================================


    if classification == "C2":


        print(
            "\n🚨 HIGH RISK ONLINE GAMBLING"
        )



    elif classification == "C1":


        print(
            "\n⚠️ SUSPICIOUS CONTENT DETECTED"
        )



    else:


        print(
            "\n✅ SAFE CONTENT"
        )



except FileNotFoundError:


    print(
        "\n❌ Image dataset tidak ditemukan"
    )


    print(
        image_path
    )



except requests.exceptions.ConnectionError:


    print(
        "\n❌ Backend tidak aktif"
    )


    print(
        "Jalankan:"
    )


    print(
        "uvicorn app.main:app --reload"
    )



except Exception as e:


    print(
        "\n❌ System Error:"
    )


    print(e)