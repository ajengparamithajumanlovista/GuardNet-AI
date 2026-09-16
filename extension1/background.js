// ============================================================
// GUARDNET-AI
// BACKGROUND SERVICE WORKER
// ============================================================

"use strict";

console.log("[GUARDNET-AI] Background service worker aktif.");


// ============================================================
// INSTALL
// ============================================================

chrome.runtime.onInstalled.addListener(() => {

    console.log(
        "[GUARDNET-AI] Extension berhasil di-install / di-update."
    );

});


// ============================================================
// MESSAGE HANDLER
// ============================================================

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        try {

            console.log(
                "[GUARDNET-AI] Background menerima message:",
                message
            );


            // ------------------------------------------------
            // PING
            // ------------------------------------------------

            if (
                message &&
                message.type === "PING"
            ) {

                sendResponse({

                    status: "success",

                    message:
                        "GuardNet-AI background aktif."

                });

                return true;
            }


            // ------------------------------------------------
            // GET STATUS
            // ------------------------------------------------

            if (
                message &&
                message.type === "GET_STATUS"
            ) {

                sendResponse({

                    status: "success",

                    extension:
                        "GuardNet-AI",

                    active:
                        true

                });

                return true;
            }


            // ------------------------------------------------
            // UNKNOWN MESSAGE
            // ------------------------------------------------

            sendResponse({

                status: "success",

                message:
                    "Message diterima."

            });

            return true;


        } catch (error) {

            console.error(
                "[GUARDNET-AI] Background error:",
                error
            );


            sendResponse({

                status: "error",

                error:
                    String(error)

            });


            return true;

        }

    }
);