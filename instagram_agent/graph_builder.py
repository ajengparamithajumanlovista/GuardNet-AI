import json



def build_graph(
    result_file="instagram_results.json"
):


    with open(
        result_file,
        "r",
        encoding="utf-8"
    ) as f:

        data=json.load(f)



    nodes=[]
    links=[]



    for item in data:


        account=item["account"]

        result=item["result"]



        post_id = (
            account
            +
            "_post"
        )



        # ACCOUNT NODE

        nodes.append({

            "id":account,

            "type":"account"

        })



        # POST NODE

        nodes.append({

            "id":post_id,

            "type":"instagram_post"

        })



        links.append({

            "source":account,

            "target":post_id,

            "relation":"uploaded"

        })




        if "entities" in result:


            entities=result["entities"]



            for threat in entities.get(
                "threat_indicator",
                []
            ):


                nodes.append({

                    "id":threat,

                    "type":"threat"

                })


                links.append({

                    "source":post_id,

                    "target":threat,

                    "relation":"contains"

                })



            for payment in entities.get(
                "payment_indicator",
                []
            ):


                nodes.append({

                    "id":payment,

                    "type":"payment"

                })


                links.append({

                    "source":post_id,

                    "target":payment,

                    "relation":"payment_indicator"

                })



    graph={

        "nodes":nodes,

        "links":links

    }



    with open(
        "threat_graph.json",
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            graph,
            f,
            indent=4,
            ensure_ascii=False
        )



    print(
        "✅ Threat Graph Created"
    )



if __name__=="__main__":

    build_graph()