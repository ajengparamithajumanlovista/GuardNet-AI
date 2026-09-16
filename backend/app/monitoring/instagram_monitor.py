import time
import requests


GUARDNET_API = "http://127.0.0.1:8000/api/detect-post"



def monitor_instagram(posts):

    print(
        "🚀 GuardNet-AI Instagram Monitoring Started"
    )


    for post in posts:


        print("\n==========================")
        print("New Instagram Post Detected")
        print("==========================")


        print("Caption:")
        print(post["caption"])



        try:


            with open(
                post["image"],
                "rb"
            ) as image_file:


                files = {

                    "image":
                    image_file

                }


                data = {

                    "caption":
                    post["caption"]

                }



                response = requests.post(

                    GUARDNET_API,

                    files=files,

                    data=data

                )



            if response.status_code != 200:


                print(
                    "❌ Backend Error:",
                    response.status_code
                )

                print(
                    response.text
                )

                continue




            result = response.json()



            print(
                "\nGuardNet-AI Result"
            )


            print(
                result
            )



            classification = result.get(
                "classification",
                {}
            )



            risk = classification.get(
                "risk_score",
                0
            )

            print(
                "RISK SCORE:",
                 risk
            )



            if risk >= 0.55:


                print(
                    "🚨 HIGH RISK JUDI ONLINE DETECTED"
                )


            elif risk >= 0.4:


                print(
                    "⚠️ Suspicious Content"
                )


            else:


                print(
                    "✅ Safe Content"
                )



        except Exception as e:


            print(
                "❌ Error:",
                e
            )



        time.sleep(5)





# ============================
# SIMULASI POST INSTAGRAM
# ============================

if __name__ == "__main__":


    posts = [

        {

            "caption":
            "Slot gacor bonus besar deposit QRIS daftar sekarang",


            "image":
            "dataset/instagram/judi1.jpg"
        }

    ]


    monitor_instagram(posts)