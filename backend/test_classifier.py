from app.models.classifier import classify_text


tests = [

    (
        "C0",
        "Hari ini pemerintah kembali melakukan edukasi bahaya judi online di masyarakat"
    ),

    (
        "C0",
        "Jangan percaya situs judi online karena dapat menyebabkan kecanduan"
    ),

    (
        "C0",
        "Polisi mengimbau masyarakat untuk menghindari perjudian online"
    ),

    (
        "C0",
        "Bahaya judi online dapat menyebabkan kerugian finansial"
    ),

    (
        "C0",
        "Penindakan terhadap jaringan judi online terus dilakukan"
    ),

    (
        "C2",
        "Slot gacor hari ini bonus besar daftar sekarang"
    ),

    (
        "C2",
        "Deposit sekarang dan dapatkan bonus member baru"
    ),

    (
        "C2",
        "Main slot gacor jackpot besar klik link di bio"
    ),

    (
        "C2",
        "Daftar judi online sekarang bonus new member"
    ),

    (
        "C2",
        "Deposit QRIS untuk mendapatkan bonus dan jackpot"
    ),

    (
        "C1",
        "Link alternatif tersedia untuk member"
    ),

    (
        "C1",
        "Promo bonus member baru tersedia hari ini"
    ),

    (
        "C1",
        "Informasi situs dan link alternatif dapat berubah"
    ),

    (
        "C1",
        "Admin menyediakan informasi pendaftaran member"
    ),

    (
        "C1",
        "Promo permainan dan bonus terbaru"
    )

]


print()
print("==============================================")
print(" GUARDNET-AI CLASSIFIER TEST")
print("==============================================")
print()


correct = 0


for index, (true_label, text) in enumerate(
    tests,
    start=1
):

    result = classify_text(
        text
    )


    predicted = result.get(
        "label"
    )


    if predicted == true_label:

        correct += 1

        status = "OK"

    else:

        status = "WRONG"


    print(
        f"{index:02d}. "
        f"TRUE={true_label} "
        f"PRED={predicted} "
        f"[{status}]"
    )

    print(
        "    Text:",
        text
    )

    print(
        "    Score:",
        result.get(
            "score"
        )
    )

    print()


accuracy = (
    correct
    /
    len(tests)
)


print("==============================================")
print(
    f"Correct: {correct}/{len(tests)}"
)

print(
    f"Smoke Accuracy: {accuracy:.2%}"
)

print("==============================================")