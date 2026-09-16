import requests
import os

from database import save_result

# ==============================
# GuardNet-AI API
# ==============================

GUARDNET_API = (
    "http://127.0.0.1:8000/api/detect-post"
)



# ==============================
# Dataset Path
# ==============================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


IMAGE_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "instagram",
    "judi1.jpg"
)



# ==============================
# Send Instagram Post
# ==============================

def analyze_instagram_post(
    image_path,
    caption
):

    print(
        "🚀 Sending Instagram Post to GuardNet-AI..."
    )


    try:

        with open(
            image_path,
            "rb"
        ) as image:


            files = {

                "image":
                image

            }


            data = {

                "caption":
                caption

            }


            response = requests.post(

                GUARDNET_API,

                files=files,

                data=data

            )


        result = response.json()


        return result



    except Exception as e:


        return {

            "error":
            str(e)

        }




# ==============================
# TEST
# ==============================

if __name__ == "__main__":


    for post in monitor_instagram():


        result = analyze_instagram_post(

            post["image"],

            post["caption"]

        )


        output = {


            "account":
            post["username"],


            "caption":
            post["caption"],


            "result":
            result

        }



        save_result(
            output
        )



        print("\n==========")
        print("GuardNet Result")
        print("==========")


        print(result)



        if "classification" in result:


            risk = result["classification"]["risk_score"]


            if risk >=0.7:

                print(
                    "🚨 HIGH RISK JUDI ONLINE"
                )


            elif risk >=0.4:

                print(
                    "⚠️ Suspicious"
                )


            else:

                print(
                    "✅ Safe"
                )


    image = IMAGE_PATH



    caption = """
    Slot gacor bonus besar
    deposit QRIS
    daftar sekarang
    """



    result = analyze_instagram_post(

        image,

        caption

    )



    print("\n==========")
    print("GuardNet Result")
    print("==========\n")



    print(result)



    if "classification" in result:


        risk = result[
            "classification"
        ][
            "risk_score"
        ]



        print(
            "\nRisk Score:",
            risk
        )



        if risk >= 0.7:

            print(
                "🚨 HIGH RISK JUDI ONLINE"
            )


        elif risk >= 0.4:

            print(
                "⚠️ Suspicious"
            )


        else:

            print(
                "✅ Safe"
            )