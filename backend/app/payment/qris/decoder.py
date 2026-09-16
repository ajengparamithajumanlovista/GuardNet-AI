import cv2
import numpy as np


# ==========================================================
# EMVCo TLV Parser
# ==========================================================

def parse_emv_tlv(payload):
    """
    Parser sederhana EMVCo TLV

    Format:
    TAG(2 digit)
    LENGTH(2 digit)
    VALUE
    """

    result = {}

    i = 0


    try:

        while i + 4 <= len(payload):

            tag = payload[i:i+2]


            length_text = payload[
                i+2:i+4
            ]


            if not length_text.isdigit():
                break


            length = int(
                length_text
            )


            start = i + 4

            end = start + length


            if end > len(payload):
                break


            value = payload[
                start:end
            ]


            result[tag] = value


            i = end


    except Exception:

        pass


    return result



# ==========================================================
# QRIS Decoder
# ==========================================================


def decode_qris(image):

    """
    QR / QRIS Intelligence Engine


    Output:

    - QR detected
    - QRIS detection
    - Merchant information
    - Payment evidence

    """


    try:


        # ==================================================
        # PIL IMAGE -> OpenCV
        # ==================================================

        img = np.array(
            image.convert("RGB")
        )


        img = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2BGR
        )



        # ==================================================
        # IMAGE PREPROCESSING
        # ==================================================

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )


        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )


        processed = cv2.cvtColor(
            gray,
            cv2.COLOR_GRAY2BGR
        )



        # ==================================================
        # QR DETECTION
        # ==================================================

        detector = cv2.QRCodeDetector()


        data, points, _ = detector.detectAndDecode(
            processed
        )



        # ==================================================
        # QR NOT FOUND
        # ==================================================

        if not data:


            return {

                "detected":
                    False,


                "is_qris":
                    False,


                "type":
                    None,


                "data":
                    None,


                "merchant_name":
                    None,


                "merchant_city":
                    None,


                "mcc":
                    None,


                "amount":
                    None,


                "evidence":
                    []

            }



        # ==================================================
        # PARSE EMV DATA
        # ==================================================

        tlv = parse_emv_tlv(
            data
        )



        merchant_name = tlv.get(
            "59"
        )


        merchant_city = tlv.get(
            "60"
        )


        mcc = tlv.get(
            "52"
        )


        amount = tlv.get(
            "54"
        )



        # ==================================================
        # QRIS IDENTIFICATION
        # ==================================================

        upper_payload = data.upper()


        is_qris = False


        qris_markers = [

            "ID.CO.QRIS",

            "QRIS",

            "ID.CO"

        ]



        for marker in qris_markers:


            if marker in upper_payload:

                is_qris = True



        # ==================================================
        # Merchant Account Information
        # ==================================================

        merchant_account_information = {}



        for tag, value in tlv.items():


            try:


                tag_number = int(tag)



                # Merchant account information
                if 26 <= tag_number <= 51:


                    merchant_account_information[
                        tag
                    ] = value



                    if "ID.CO.QRIS" in value.upper():

                        is_qris = True



            except Exception:

                continue



        # ==================================================
        # Evidence Builder
        # ==================================================

        evidence = [

            "qr_code"

        ]


        if is_qris:

            evidence.append(
                "qris"
            )


        if merchant_name:

            evidence.append(
                "merchant_data"
            )


        if amount:

            evidence.append(
                "amount_information"
            )



        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        return {


            "detected":

                True,


            "is_qris":

                is_qris,


            "type":

                "QRIS"
                if is_qris
                else "QR",



            "data":

                data,



            "merchant_name":

                merchant_name,



            "merchant_city":

                merchant_city,



            "mcc":

                mcc,



            "amount":

                amount,



            "merchant_account_information":

                merchant_account_information,



            "emv_tags":

                tlv,



            "evidence":

                evidence

        }



    except Exception as e:



        return {


            "detected":

                False,


            "is_qris":

                False,


            "type":

                None,


            "data":

                None,


            "merchant_name":

                None,


            "merchant_city":

                None,


            "mcc":

                None,


            "amount":

                None,


            "evidence":

                [],


            "error":

                str(e)

        }