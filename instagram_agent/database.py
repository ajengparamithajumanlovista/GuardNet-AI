import json
import os


RESULT_FILE = (
    "instagram_results.json"
)



def save_result(data):

    results = []


    if os.path.exists(
        RESULT_FILE
    ):

        with open(
            RESULT_FILE,
            "r"
        ) as f:

            results = json.load(f)



    results.append(data)



    with open(
        RESULT_FILE,
        "w"
    ) as f:

        json.dump(
            results,
            f,
            indent=4
        )