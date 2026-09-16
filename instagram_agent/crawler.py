import json
import time
from instagram_agent import analyze_instagram_post
from instagram_agent import analyze_instagram_post


posts = [

{
"account":"@slot_gacor123",
"image":"dataset/instagram/judi1.jpg",
"caption":"🔥 Slot gacor bonus besar deposit QRIS daftar sekarang"
},


{
"account":"@travel_indonesia",
"image":"dataset/instagram/safe.jpg",
"caption":"Liburan indah bersama keluarga di pantai"
}


]



results=[]



print("🔍 Instagram Monitoring Started...")


for post in posts:


    print(
        "\nChecking:",
        post["account"]
    )


    result = analyze_instagram_post(
        post["image"],
        post["caption"]
    )


    results.append({

        "account":
        post["account"],


        "caption":
        post["caption"],


        "result":
        result

    })


    time.sleep(2)



with open(
"instagram_results.json",
"w",
encoding="utf-8"

) as f:


    json.dump(
        results,
        f,
        indent=4,
        ensure_ascii=False
    )



print(
"\n✅ Monitoring Finished"
)

print(
"Saved: instagram_results.json"
)