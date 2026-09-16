// ============================================================
// GUARDNET-AI
// INSTAGRAM REAL-TIME CONTENT MONITOR
// ============================================================
//
// Fungsi:
// 1. Mendeteksi posting Instagram yang terlihat di layar
// 2. Mengambil teks/caption
// 3. Mengambil komentar yang terlihat
// 4. Mengambil gambar posting
// 5. Mengirim data ke backend GuardNet-AI
// 6. Menampilkan C0 / C1 / C2
// 7. Bekerja otomatis ketika user melakukan scroll
//
// Backend:
// http://127.0.0.1:8000/analyze
// ============================================================

(() => {

    "use strict";

    console.log(
        "%c[GuardNet-AI] Instagram monitor starting...",
        "color:#00ffcc;font-weight:bold;"
    );


    // ========================================================
    // CONFIGURATION
    // ========================================================

    const BACKEND_URL =
        "http://127.0.0.1:8000/analyze";

    const SCAN_INTERVAL =
        1500;

    const MAX_COMMENTS =
        30;

    const processedPosts =
        new Map();


    // ========================================================
    // UTILITY
    // ========================================================

    function sleep(ms) {

        return new Promise(
            resolve => setTimeout(resolve, ms)
        );

    }


    function cleanText(text) {

        if (!text) {
            return "";
        }

        return String(text)
            .replace(/\s+/g, " ")
            .trim();

    }


    function getPostKey(post) {

        try {

            const links =
                Array.from(
                    post.querySelectorAll("a[href]")
                );

            for (const link of links) {

                const href =
                    link.getAttribute("href");

                if (
                    href &&
                    (
                        href.includes("/p/") ||
                        href.includes("/reel/")
                    )
                ) {

                    return href;

                }

            }

        } catch (error) {}

        // fallback
        return (
            "post-" +
            Math.random()
                .toString(36)
                .substring(2)
        );

    }


    // ========================================================
    // FIND INSTAGRAM POST
    // ========================================================

    function getPosts() {

        const posts =
            Array.from(
                document.querySelectorAll("article")
            );

        return posts;

    }


    // ========================================================
    // EXTRACT CAPTION + VISIBLE COMMENTS
    // ========================================================

    function extractPostText(post) {

        const textParts = [];


        // ----------------------------------------------------
        // ALL VISIBLE TEXT
        // ----------------------------------------------------

        const visibleText =
            cleanText(
                post.innerText || ""
            );


        if (visibleText) {

            textParts.push(
                visibleText
            );

        }


        // ----------------------------------------------------
        // COMMENTS
        // ----------------------------------------------------

        const comments = [];


        const commentCandidates =
            Array.from(
                post.querySelectorAll(
                    "ul li"
                )
            );


        for (
            const element
            of commentCandidates
        ) {

            const text =
                cleanText(
                    element.innerText || ""
                );


            if (
                text &&
                !comments.includes(text)
            ) {

                comments.push(text);

            }


            if (
                comments.length >=
                MAX_COMMENTS
            ) {

                break;

            }

        }


        // ----------------------------------------------------
        // ADD COMMENTS SEPARATELY
        // ----------------------------------------------------

        if (comments.length > 0) {

            textParts.push(
                "[COMMENTS] " +
                comments.join(" | ")
            );

        }


        // ----------------------------------------------------
        // FINAL TEXT
        // ----------------------------------------------------

        return cleanText(
            textParts.join(" ")
        );

    }


    // ========================================================
    // EXTRACT IMAGE
    // ========================================================

    function getPostImage(post) {

        const images =
            Array.from(
                post.querySelectorAll("img")
            );


        if (
            images.length === 0
        ) {

            return null;

        }


        // pilih gambar terbesar
        let bestImage = null;
        let bestArea = 0;


        for (
            const image
            of images
        ) {

            const width =
                image.naturalWidth ||
                image.width ||
                0;

            const height =
                image.naturalHeight ||
                image.height ||
                0;

            const area =
                width * height;


            if (
                area > bestArea
            ) {

                bestArea =
                    area;

                bestImage =
                    image;

            }

        }


        return (
            bestImage ||
            images[0]
        );

    }


    // ========================================================
    // IMAGE URL
    // ========================================================

    function getImageURL(image) {

        if (!image) {
            return null;
        }


        return (
            image.currentSrc ||
            image.src ||
            image.getAttribute("src")
        );

    }


    // ========================================================
    // FETCH IMAGE
    // ========================================================

    async function imageURLToBlob(url) {

        if (!url) {

            return null;

        }


        try {

            const response =
                await fetch(
                    url,
                    {
                        method: "GET",
                        credentials: "include"
                    }
                );


            if (!response.ok) {

                console.warn(
                    "[GuardNet-AI] Image fetch failed:",
                    response.status
                );

                return null;

            }


            return await response.blob();

        } catch (error) {

            console.warn(
                "[GuardNet-AI] Cannot fetch image:",
                error
            );

            return null;

        }

    }


    // ========================================================
    // SEND TO BACKEND
    // ========================================================

    async function analyzePost(
        post,
        postKey
    ) {

        if (
            processedPosts.has(
                postKey
            )
        ) {

            return;

        }


        processedPosts.set(
            postKey,
            "processing"
        );


        console.log(
            "[GuardNet-AI] Analyzing:",
            postKey
        );


        // ----------------------------------------------------
        // TEXT
        // ----------------------------------------------------

        const captionAndComments =
            extractPostText(post);


        console.log(
            "[GuardNet-AI] Caption + comments:",
            captionAndComments
        );


        // ----------------------------------------------------
        // IMAGE
        // ----------------------------------------------------

        const image =
            getPostImage(post);


        const imageURL =
            getImageURL(image);


        let imageBlob =
            null;


        if (imageURL) {

            imageBlob =
                await imageURLToBlob(
                    imageURL
                );

        }


        // ----------------------------------------------------
        // FORM DATA
        // ----------------------------------------------------

        const formData =
            new FormData();


        if (imageBlob) {

            formData.append(
                "image",
                imageBlob,
                "instagram_post.jpg"
            );

        }


        formData.append(
            "caption",
            captionAndComments
        );


        // ----------------------------------------------------
        // BACKEND REQUEST
        // ----------------------------------------------------

        try {

            const response =
                await fetch(
                    BACKEND_URL,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Backend HTTP " +
                    response.status
                );

            }


            const result =
                await response.json();


            console.log(
                "%c[GuardNet-AI] Backend result:",
                "color:#00ffcc;font-weight:bold;",
                result
            );


            processedPosts.set(
                postKey,
                result
            );


            displayResult(
                post,
                result
            );


        } catch (error) {

            console.error(
                "[GuardNet-AI] Backend error:",
                error
            );


            processedPosts.set(
                postKey,
                "error"
            );


            displayError(
                post,
                error
            );

        }

    }


    // ========================================================
    // EXTRACT CLASSIFICATION
    // ========================================================

    function getClassification(result) {

        if (!result) {

            return {
                label: "UNKNOWN",
                score: 0,
                confidence: 0
            };

        }


        let classification =
            result.classification;


        // ----------------------------------------------------
        // Backend format:
        //
        // classification:
        // {
        //    classification: "C1",
        //    risk_score: 0.469,
        //    confidence: 0.553
        // }
        // ----------------------------------------------------

        if (
            classification &&
            typeof classification ===
            "object"
        ) {

            return {

                label:
                    classification.classification ||
                    "UNKNOWN",

                score:
                    Number(
                        classification.risk_score ||
                        0
                    ),

                confidence:
                    Number(
                        classification.confidence ||
                        0
                    )

            };

        }


        // ----------------------------------------------------
        // fallback
        // ----------------------------------------------------

        if (
            typeof classification ===
            "string"
        ) {

            return {

                label:
                    classification,

                score:
                    Number(
                        result.risk_score ||
                        0
                    ),

                confidence:
                    Number(
                        result.confidence ||
                        0
                    )

            };

        }


        return {

            label: "UNKNOWN",

            score: 0,

            confidence: 0

        };

    }


    // ========================================================
    // LABEL INFORMATION
    // ========================================================

    function getLabelInfo(label) {

        switch (label) {

            case "C2":

                return {

                    title:
                        "HIGH RISK",

                    description:
                        "Indikasi kuat promosi judi online",

                    icon:
                        "🚨"

                };


            case "C1":

                return {

                    title:
                        "SUSPICIOUS",

                    description:
                        "Terdapat indikator mencurigakan",

                    icon:
                        "⚠️"

                };


            case "C0":

                return {

                    title:
                        "LOW RISK",

                    description:
                        "Tidak ditemukan indikasi kuat",

                    icon:
                        "✓"

                };


            default:

                return {

                    title:
                        "UNKNOWN",

                    description:
                        "Hasil belum tersedia",

                    icon:
                        "?"

                };

        }

    }


    // ========================================================
    // CREATE RESULT BADGE
    // ========================================================

    function createBadge() {

        const badge =
            document.createElement(
                "div"
            );


        badge.className =
            "guardnet-ai-result";


        badge.style.position =
            "absolute";


        badge.style.top =
            "10px";


        badge.style.right =
            "10px";


        badge.style.zIndex =
            "999999";


        badge.style.width =
            "280px";


        badge.style.padding =
            "14px";


        badge.style.borderRadius =
            "14px";


        badge.style.background =
            "#062c25";


        badge.style.color =
            "white";


        badge.style.fontFamily =
            "Arial, sans-serif";


        badge.style.boxShadow =
            "0 8px 30px rgba(0,0,0,.35)";


        badge.style.fontSize =
            "13px";


        return badge;

    }


    // ========================================================
    // DISPLAY RESULT
    // ========================================================

    function displayResult(
        post,
        result
    ) {

        // remove old badge
        const oldBadge =
            post.querySelector(
                ".guardnet-ai-result"
            );


        if (oldBadge) {

            oldBadge.remove();

        }


        const data =
            getClassification(
                result
            );


        const info =
            getLabelInfo(
                data.label
            );


        const badge =
            createBadge();


        const scorePercent =
            Math.round(
                data.score * 100
            );


        const confidencePercent =
            Math.round(
                data.confidence * 100
            );


        badge.innerHTML = `

            <div style="
                font-size:16px;
                font-weight:700;
                margin-bottom:8px;
            ">
                GUARDNET-AI
            </div>

            <div style="
                font-size:18px;
                font-weight:700;
                margin-bottom:5px;
            ">
                ${info.icon}
                ${data.label}
                -
                ${scorePercent}%
                risk
            </div>

            <div style="
                font-size:13px;
                opacity:.9;
                margin-bottom:8px;
            ">
                ${info.title}
            </div>

            <div style="
                font-size:12px;
                opacity:.85;
                margin-bottom:8px;
            ">
                ${info.description}
            </div>

            <div style="
                font-size:12px;
                opacity:.8;
            ">
                Confidence:
                ${confidencePercent}%
            </div>

        `;


        // ----------------------------------------------------
        // Make post position relative
        // ----------------------------------------------------

        const computed =
            window.getComputedStyle(
                post
            );


        if (
            computed.position ===
            "static"
        ) {

            post.style.position =
                "relative";

        }


        post.appendChild(
            badge
        );

    }


    // ========================================================
    // ERROR DISPLAY
    // ========================================================

    function displayError(
        post,
        error
    ) {

        const oldBadge =
            post.querySelector(
                ".guardnet-ai-result"
            );


        if (oldBadge) {

            oldBadge.remove();

        }


        const badge =
            createBadge();


        badge.innerHTML = `

            <div style="
                font-size:16px;
                font-weight:700;
                margin-bottom:8px;
            ">
                GUARDNET-AI
            </div>

            <div style="
                font-size:15px;
                font-weight:700;
                color:#ff8a8a;
            ">
                Backend Error
            </div>

            <div style="
                font-size:11px;
                margin-top:6px;
                opacity:.8;
            ">
                Pastikan backend berjalan
                di 127.0.0.1:8000
            </div>

        `;


        const computed =
            window.getComputedStyle(
                post
            );


        if (
            computed.position ===
            "static"
        ) {

            post.style.position =
                "relative";

        }


        post.appendChild(
            badge
        );

    }


    // ========================================================
    // PROCESS VISIBLE POSTS
    // ========================================================

    async function scanPosts() {

        const posts =
            getPosts();


        console.log(
            "[GuardNet-AI] Visible posts:",
            posts.length
        );


        for (
            const post
            of posts
        ) {

            // ------------------------------------------------
            // Check visibility
            // ------------------------------------------------

            const rect =
                post.getBoundingClientRect();


            const visible =
                rect.bottom > 0 &&
                rect.top <
                window.innerHeight;


            if (!visible) {

                continue;

            }


            // ------------------------------------------------
            // Create stable key
            // ------------------------------------------------

            const postKey =
                getPostKey(
                    post
                );


            if (
                processedPosts.has(
                    postKey
                )
            ) {

                continue;

            }


            // ------------------------------------------------
            // Analyze
            // ------------------------------------------------

            await analyzePost(
                post,
                postKey
            );

        }

    }


    // ========================================================
    // MUTATION OBSERVER
    // ========================================================

    const observer =
        new MutationObserver(
            () => {

                clearTimeout(
                    window.__guardnetScanTimer
                );


                window.__guardnetScanTimer =
                    setTimeout(
                        () => {

                            scanPosts();

                        },
                        700
                    );

            }
        );


    observer.observe(
        document.body,
        {
            childList: true,
            subtree: true
        }
    );


    // ========================================================
    // SCROLL MONITOR
    // ========================================================

    let scrollTimer =
        null;


    window.addEventListener(
        "scroll",
        () => {

            clearTimeout(
                scrollTimer
            );


            scrollTimer =
                setTimeout(
                    () => {

                        scanPosts();

                    },
                    500
                );

        },
        {
            passive: true
        }
    );


    // ========================================================
    // PERIODIC SCAN
    // ========================================================

    setInterval(
        () => {

            scanPosts();

        },
        SCAN_INTERVAL
    );


    // ========================================================
    // INITIAL START
    // ========================================================

    async function start() {

        console.log(
            "%c[GuardNet-AI] Instagram monitor aktif.",
            "color:#00ffcc;font-weight:bold;font-size:14px;"
        );


        console.log(
            "[GuardNet-AI] Backend:",
            BACKEND_URL
        );


        await sleep(
            2000
        );


        scanPosts();

    }


    start();

})();