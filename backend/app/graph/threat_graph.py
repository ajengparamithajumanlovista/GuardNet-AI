# ============================================================
# GUARDNET-AI
# THREAT ENTITY GRAPH BUILDER
# ============================================================


def add_node(
    nodes,
    node_id,
    node_type,
    value
):

    existing = {

        node.get("id")

        for node in nodes

    }


    if node_id not in existing:

        nodes.append({

            "id":
                node_id,

            "type":
                node_type,

            "value":
                value

        })


def add_link(
    links,
    source,
    target,
    relation
):

    links.append({

        "source":
            source,

        "target":
            target,

        "relation":
            relation

    })


# ============================================================
# BUILD GRAPH FROM CASES
# ============================================================

def build_threat_graph(
    cases
):

    nodes = []

    links = []


    # ========================================================
    # CASE NODES
    # ========================================================

    for case in cases:

        case_id = case.get(
            "case_id"
        )


        if not case_id:

            continue


        case_node = (
            "case:" + case_id
        )


        add_node(

            nodes,

            case_node,

            "case",

            case_id

        )


        # ====================================================
        # DIGITAL INTELLIGENCE
        # ====================================================

        digital = case.get(
            "digital_intelligence",
            {}
        )


        # ----------------------------------------------------
        # ACCOUNT
        # ----------------------------------------------------

        for account in digital.get(
            "account",
            []
        ):

            node_id = (
                "account:" +
                account.lower()
            )


            add_node(

                nodes,

                node_id,

                "account",

                account

            )


            add_link(

                links,

                case_node,

                node_id,

                "has_account"

            )


        # ----------------------------------------------------
        # DOMAIN
        # ----------------------------------------------------

        for domain in digital.get(
            "domain",
            []
        ):

            node_id = (
                "domain:" +
                domain.lower()
            )


            add_node(

                nodes,

                node_id,

                "domain",

                domain

            )


            add_link(

                links,

                case_node,

                node_id,

                "contains_domain"

            )


        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        for url in digital.get(
            "url",
            []
        ):

            node_id = (
                "url:" +
                url.lower()
            )


            add_node(

                nodes,

                node_id,

                "url",

                url

            )


            add_link(

                links,

                case_node,

                node_id,

                "contains_url"

            )


        # ----------------------------------------------------
        # CONTACT
        # ----------------------------------------------------

        for contact in digital.get(
            "contact",
            []
        ):

            node_id = (
                "contact:" +
                contact
            )


            add_node(

                nodes,

                node_id,

                "contact",

                contact

            )


            add_link(

                links,

                case_node,

                node_id,

                "contains_contact"

            )


        # ====================================================
        # PAYMENT
        # ====================================================

        payment = case.get(
            "payment",
            {}
        )


        for indicator in payment.get(
            "evidence",
            []
        ):

            indicator = str(
                indicator
            ).lower()


            node_id = (
                "payment:" +
                indicator
            )


            add_node(

                nodes,

                node_id,

                "payment",

                indicator

            )


            add_link(

                links,

                case_node,

                node_id,

                "payment_indicator"

            )


        # ====================================================
        # QRIS
        # ====================================================

        qris = case.get(
            "qris",
            {}
        )


        if qris.get(
            "detected",
            False
        ):

            node_id = (
                "payment:qris"
            )


            add_node(

                nodes,

                node_id,

                "payment",

                "QRIS"

            )


            add_link(

                links,

                case_node,

                node_id,

                "payment_indicator"

            )


    # ========================================================
    # CASE-TO-CASE SHARED INDICATORS
    # ========================================================

    for index, case_a in enumerate(
        cases
    ):

        case_a_id = case_a.get(
            "case_id"
        )


        if not case_a_id:

            continue


        case_a_node = (
            "case:" +
            case_a_id
        )


        for case_b in cases[
            index + 1:
        ]:

            case_b_id = case_b.get(
                "case_id"
            )


            if not case_b_id:

                continue


            case_b_node = (
                "case:" +
                case_b_id
            )


            # -----------------------------------------------
            # Collect indicators
            # -----------------------------------------------

            def indicators(case):

                digital = case.get(
                    "digital_intelligence",
                    {}
                )


                result = set()


                for key in [

                    "account",

                    "domain",

                    "url",

                    "contact"

                ]:

                    for value in digital.get(
                        key,
                        []
                    ):

                        result.add(

                            (
                                key,

                                str(value).lower()

                            )

                        )


                payment = case.get(
                    "payment",
                    {}
                )


                for value in payment.get(
                    "evidence",
                    []
                ):

                    result.add(

                        (
                            "payment",

                            str(value).lower()

                        )

                    )


                return result


            indicators_a = indicators(
                case_a
            )


            indicators_b = indicators(
                case_b
            )


            shared = (
                indicators_a &
                indicators_b
            )


            # -----------------------------------------------
            # Create correlation links
            # -----------------------------------------------

            for indicator_type, value in shared:

                node_id = (
                    indicator_type +
                    ":" +
                    value
                )


                add_link(

                    links,

                    case_a_node,

                    node_id,

                    "shared_indicator"

                )


                add_link(

                    links,

                    case_b_node,

                    node_id,

                    "shared_indicator"

                )


    return {

        "nodes":
            nodes,

        "links":
            links,

        "node_count":
            len(nodes),

        "link_count":
            len(links),

        "status":
            "success"

    }