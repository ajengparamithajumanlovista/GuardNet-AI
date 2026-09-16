// ============================================================
// GUARDNET-AI
// INSTAGRAM REAL-TIME MONITOR
// TEXT + CAPTION + COMMENTS + RISK + EVIDENCE
// ============================================================

(() => {
    "use strict";

    // ========================================================
    // CONFIGURATION
    // ========================================================

    const BACKEND_URL =
        "http://127.0.0.1:8000/analyze";

    const SCAN_INTERVAL = 2000;
    const SCROLL_DELAY = 700;
    const MUTATION_DELAY = 1000;

    const MAX_COMMENTS = 30;
    const MAX_TEXT_LENGTH = 12000;

    const processedPosts = new Map();

    let scanRunning = false;
    let mutationTimer = null;
    let scrollTimer = null;

    // ========================================================
    // START MESSAGE
    // ========================================================

    console.log(
        "%c[GUARDNET-AI] Extension aktif",
        "color:#00d9a5;font-size:16px;font-weight:bold;"
    );

    console.log(
        "[GUARDNET-AI] Backend:",
        BACKEND_URL
    );

    // ========================================================
    // TEXT CLEANING
    // ========================================================

    function cleanText(text) {

        if (!text) {
            return "";
        }

        return String(text)
            .replace(/\u00a0/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    }

    // ========================================================
    // NORMALIZATION
    // ========================================================

    function normalizeForCompare(text) {

        return cleanText(text)
            .toLowerCase()
            .replace(
                /[^\p{L}\p{N}\s@._:/-]/gu,
                " "
            )
            .replace(/\s+/g, " ")
            .trim();
    }

    // ========================================================
    // UI TEXT DETECTION
    // ========================================================

    function isUiText(text) {

        const value =
            cleanText(text).toLowerCase();

        if (!value) {
            return true;
        }

        const exactUi =
            new Set([
                "like",
                "comment",
                "comments",
                "share",
                "follow",
                "following",
                "message",
                "send message",
                "translate",
                "see translation",
                "lihat terjemahan",
                "reply",
                "balas",
                "more",
                "see more",
                "lihat selengkapnya",
                "original audio",
                "audio asli",
                "reels",
                "verified",
                "sponsored",
                "ad"
            ]);

        if (exactUi.has(value)) {
            return true;
        }

        if (
            /^(like|likes|comment|comments|reply|replies)\s*\d*$/i
                .test(value)
        ) {
            return true;
        }

        if (
            /^\d+([.,]\d+)?[kmb]?\s*(likes?|comments?)?$/i
                .test(value)
        ) {
            return true;
        }

        if (
            /^\d+\s*(s|m|h|d|w|mo|y)$/i
                .test(value)
        ) {
            return true;
        }

        if (
            /^\d+\s*(menit|jam|hari|minggu|bulan|tahun)$/i
                .test(value)
        ) {
            return true;
        }

        return false;
    }

    // ========================================================
    // TIME / COUNT DETECTION
    // ========================================================

    function isLikelyTimeOrCount(text) {

        const value =
            cleanText(text).toLowerCase();

        return (
            /^\d+\s*(s|m|h|d|w|mo|y)$/i.test(value) ||
            /^\d+\s*(menit|jam|hari|minggu|bulan|tahun)$/i.test(value) ||
            /^\d+([.,]\d+)?[kmb]?$/.test(value)
        );
    }

    // ========================================================
    // USERNAME DETECTION
    // ========================================================

    function looksLikeUsername(text) {

        const value =
            cleanText(text);

        if (!value || value.length > 80) {
            return false;
        }

        if (value.startsWith("@")) {
            return true;
        }

        if (
            !value.includes(" ") &&
            /^[a-zA-Z0-9._]+$/.test(value)
        ) {
            return true;
        }

        return false;
    }

    // ========================================================
    // UNIQUE TEXT
    // ========================================================

    function uniqueTexts(items) {

        const seen = new Set();
        const output = [];

        for (const item of items) {

            const text =
                cleanText(item);

            const key =
                normalizeForCompare(text);

            if (!key || seen.has(key)) {
                continue;
            }

            seen.add(key);
            output.push(text);
        }

        return output;
    }

    // ========================================================
    // FIND INSTAGRAM POSTS
    // ========================================================

    function getPosts() {

        return Array.from(
            document.querySelectorAll("article")
        );
    }

    // ========================================================
    // VISIBILITY CHECK
    // ========================================================

    function isVisible(element) {

        if (!element) {
            return false;
        }

        const rect =
            element.getBoundingClientRect();

        return (
            rect.bottom > 0 &&
            rect.top < window.innerHeight &&
            rect.right > 0 &&
            rect.left < window.innerWidth
        );
    }

    // ========================================================
    // POST KEY
    // ========================================================

    function getPostKey(post) {

        try {

            const links =
                Array.from(
                    post.querySelectorAll(
                        'a[href*="/p/"], ' +
                        'a[href*="/reel/"], ' +
                        'a[href*="/tv/"]'
                    )
                );

            for (const link of links) {

                const href =
                    link.getAttribute("href");

                if (href) {

                    return href.split("?")[0];
                }
            }

        } catch (error) {

            console.warn(
                "[GUARDNET-AI] Gagal mendapatkan post ID:",
                error
            );
        }

        const fallback =
            cleanText(
                post.innerText || ""
            ).substring(0, 300);

        return (
            "post_" +
            normalizeForCompare(fallback)
                .replace(/\W+/g, "_")
                .substring(0, 120)
        );
    }

    // ========================================================
    // CAPTION EXTRACTION
    // ========================================================

    function extractCaption(post) {

        const candidates = [];

        const elements =
            Array.from(
                post.querySelectorAll(
                    "span, div"
                )
            );

        for (const element of elements) {

            const text =
                cleanText(
                    element.innerText || ""
                );

            if (
                !text ||
                text.length < 3 ||
                text.length > 1000
            ) {
                continue;
            }

            if (isUiText(text)) {
                continue;
            }

            if (
                isLikelyTimeOrCount(text)
            ) {
                continue;
            }

            if (
                text.split(" ").length > 180
            ) {
                continue;
            }

            const lower =
                text.toLowerCase();

            if (
                lower === "see more" ||
                lower === "lihat selengkapnya"
            ) {
                continue;
            }

            if (
                lower === "original audio" ||
                lower === "audio asli"
            ) {
                continue;
            }

            candidates.push(text);
        }

        const unique =
            uniqueTexts(candidates);

        if (unique.length === 0) {
            return "";
        }

        /*
         * Prioritaskan teks yang:
         * - cukup panjang
         * - memiliki beberapa kata
         * - bukan username
         */

        unique.sort((a, b) => {

            const score = (text) => {

                let value = 0;

                if (text.includes(" ")) {
                    value += 20;
                }

                value +=
                    Math.min(
                        text.length,
                        500
                    );

                if (
                    looksLikeUsername(text)
                ) {
                    value -= 100;
                }

                return value;
            };

            return score(b) - score(a);
        });

        return cleanText(
            unique[0] || ""
        );
    }

    // ========================================================
    // COMMENT CLEANING
    // ========================================================

    function cleanCommentCandidate(text) {

        const raw =
            cleanText(text);

        if (
            !raw ||
            raw.length < 2
        ) {
            return "";
        }

        const lines =
            raw
                .split(/\n+/)
                .map(cleanText)
                .filter(Boolean);

        if (lines.length === 0) {
            return "";
        }

        const useful = [];

        for (const line of lines) {

            if (isUiText(line)) {
                continue;
            }

            if (
                isLikelyTimeOrCount(line)
            ) {
                continue;
            }

            const lower =
                line.toLowerCase();

            const ignored =
                [
                    "follow",
                    "following",
                    "reply",
                    "balas",
                    "translate",
                    "lihat terjemahan",
                    "see translation",
                    "like",
                    "likes",
                    "view all",
                    "lihat semua"
                ];

            if (
                ignored.includes(lower)
            ) {
                continue;
            }

            useful.push(line);
        }

        if (useful.length === 0) {
            return "";
        }

        // Buang username pertama.
        if (
            useful.length >= 2 &&
            looksLikeUsername(
                useful[0]
            )
        ) {
            useful.shift();
        }

        // Buang username kedua jika ada.
        if (
            useful.length >= 2 &&
            looksLikeUsername(
                useful[0]
            )
        ) {
            useful.shift();
        }

        if (useful.length === 0) {
            return "";
        }

        const result =
            cleanText(
                useful.join(" ")
            );

        if (result.length < 2) {
            return "";
        }

        if (isUiText(result)) {
            return "";
        }

        return result.substring(
            0,
            800
        );
    }

    // ========================================================
    // COMMENT EXTRACTION
    // ========================================================

    function extractComments(post) {

        const comments = [];

        // ----------------------------------------------------
        // METHOD 1 - LI
        // ----------------------------------------------------

        const liElements =
            Array.from(
                post.querySelectorAll(
                    "ul li"
                )
            );

        for (
            const li of liElements
        ) {

            const candidate =
                cleanCommentCandidate(
                    li.innerText || ""
                );

            if (
                candidate &&
                !comments.some(
                    (item) =>
                        normalizeForCompare(
                            item
                        ) ===
                        normalizeForCompare(
                            candidate
                        )
                )
            ) {

                comments.push(
                    candidate
                );
            }

            if (
                comments.length >=
                MAX_COMMENTS
            ) {
                break;
            }
        }

        // ----------------------------------------------------
        // METHOD 2 - ROLE
        // ----------------------------------------------------

        if (
            comments.length < 3
        ) {

            const roleElements =
                Array.from(
                    post.querySelectorAll(
                        '[role="comment"], ' +
                        '[aria-label*="comment" i]'
                    )
                );

            for (
                const element of roleElements
            ) {

                const candidate =
                    cleanCommentCandidate(
                        element.innerText || ""
                    );

                if (
                    candidate &&
                    !comments.some(
                        (item) =>
                            normalizeForCompare(
                                item
                            ) ===
                            normalizeForCompare(
                                candidate
                            )
                    )
                ) {

                    comments.push(
                        candidate
                    );
                }

                if (
                    comments.length >=
                    MAX_COMMENTS
                ) {
                    break;
                }
            }
        }

        // ----------------------------------------------------
        // METHOD 3 - FALLBACK TEXT BLOCK
        // ----------------------------------------------------

        if (
            comments.length < 3
        ) {

            const blocks =
                Array.from(
                    post.querySelectorAll(
                        "div"
                    )
                );

            for (
                const block of blocks
            ) {

                const text =
                    cleanText(
                        block.innerText || ""
                    );

                if (
                    !text ||
                    text.length < 5 ||
                    text.length > 800
                ) {
                    continue;
                }

                if (
                    text.split("\n").length < 2
                ) {
                    continue;
                }

                const candidate =
                    cleanCommentCandidate(
                        text
                    );

                if (
                    candidate &&
                    !comments.some(
                        (item) =>
                            normalizeForCompare(
                                item
                            ) ===
                            normalizeForCompare(
                                candidate
                            )
                    )
                ) {

                    comments.push(
                        candidate
                    );
                }

                if (
                    comments.length >=
                    MAX_COMMENTS
                ) {
                    break;
                }
            }
        }

        return comments.slice(
            0,
            MAX_COMMENTS
        );
    }

    // ========================================================
    // EXTRACT POST CONTENT
    // ========================================================

    function extractPostContent(post) {

        const caption =
            extractCaption(post);

        const comments =
            extractComments(post);

        const sections = [];

        if (caption) {

            sections.push(
                "[CAPTION]\n" +
                caption
            );
        }

        if (
            comments.length > 0
        ) {

            sections.push(
                "[COMMENTS]\n" +
                comments.join("\n")
            );
        }

        let finalText =
            sections.join(
                "\n\n"
            );

        if (
            finalText.length >
            MAX_TEXT_LENGTH
        ) {

            finalText =
                finalText.substring(
                    0,
                    MAX_TEXT_LENGTH
                );
        }

        console.log(
            "[GUARDNET-AI] Caption:",
            caption
        );

        console.log(
            "[GUARDNET-AI] Comments:",
            comments
        );

        console.log(
            "[GUARDNET-AI] Combined text:",
            finalText
        );

        return {
            caption,
            comments,
            text: finalText
        };
    }

    // ========================================================
    // CREATE BADGE
    // ========================================================

    function createBadge() {

        const badge =
            document.createElement(
                "div"
            );

        badge.className =
            "guardnet-ai-badge";

        Object.assign(
            badge.style,
            {
                position: "absolute",
                top: "10px",
                right: "10px",
                zIndex: "999999",
                width: "310px",
                maxWidth: "calc(100% - 20px)",
                boxSizing: "border-box",
                padding: "15px",
                borderRadius: "15px",
                background:
                    "linear-gradient(135deg,#062c25,#073c31)",
                color: "#ffffff",
                fontFamily:
                    "Arial, sans-serif",
                boxShadow:
                    "0 8px 30px rgba(0,0,0,.45)",
                pointerEvents:
                    "none",
                lineHeight:
                    "1.4",
                backdropFilter:
                    "blur(8px)"
            }
        );

        return badge;
    }

    // ========================================================
    // LABEL INFORMATION
    // ========================================================

    function getLabelInfo(label) {

        if (label === "C2") {

            return {
                icon: "🚨",
                title: "HIGH RISK",
                description:
                    "Indikasi kuat promosi atau aktivitas judi online."
            };
        }

        if (label === "C1") {

            return {
                icon: "⚠️",
                title: "SUSPICIOUS",
                description:
                    "Terdapat indikator mencurigakan yang memerlukan perhatian."
            };
        }

        if (label === "C0") {

            return {
                icon: "✓",
                title: "LOW RISK",
                description:
                    "Tidak ditemukan indikasi kuat aktivitas judi online."
            };
        }

        return {
            icon: "❔",
            title: "UNKNOWN",
            description:
                "Hasil analisis belum tersedia."
        };
    }

    // ========================================================
    // PARSE BACKEND RESULT
    // ========================================================

    function parseResult(result) {

        console.log(
            "[GUARDNET-AI] Parsing result:",
            result
        );

        // ----------------------------------------------------
        // VALIDATE ROOT
        // ----------------------------------------------------

        if (
            !result ||
            typeof result !== "object"
        ) {

            return {
                label: "UNKNOWN",
                confidence: 0,
                riskScore: 0,
                evidence: null
            };
        }

        /*
         * Backend normal:
         *
         * {
         *   classification: {
         *      label: "C2",
         *      score: 0.85,
         *      confidence: 0.85,
         *      probabilities: {...},
         *      evidence: {...}
         *   }
         * }
         *
         * Tetapi kita juga dukung:
         * result.data
         * result.result
         * result.classification
         */

        let source =
            result;

        if (
            result.data &&
            typeof result.data === "object"
        ) {

            source =
                result.data;
        }

        if (
            source.result &&
            typeof source.result === "object"
        ) {

            source =
                source.result;
        }

        let classification =
            source.classification;

        if (
            !classification ||
            typeof classification !== "object"
        ) {

            // Kemungkinan backend langsung
            // mengirim label/score.

            classification =
                source;
        }

        // ----------------------------------------------------
        // LABEL
        // ----------------------------------------------------

        let label =
            classification.label ||
            classification.classification ||
            source.label ||
            source.classification ||
            "UNKNOWN";

        // Jika classification berupa string.
        if (
            typeof label !== "string"
        ) {

            label =
                String(label);
        }

        label =
            label.trim();

        // ----------------------------------------------------
        // CONFIDENCE
        // ----------------------------------------------------

        let confidence =
            Number(
                classification.confidence
            );

        // Fallback probability terbesar.
        if (
            !Number.isFinite(
                confidence
            ) &&
            classification.probabilities &&
            typeof classification.probabilities === "object"
        ) {

            const values =
                Object.values(
                    classification.probabilities
                )
                .map(Number)
                .filter(
                    Number.isFinite
                );

            if (
                values.length > 0
            ) {

                confidence =
                    Math.max(
                        ...values
                    );
            }
        }

        // Fallback score.
        if (
            !Number.isFinite(
                confidence
            )
        ) {

            confidence =
                Number(
                    classification.score
                );
        }

        // Fallback source confidence.
        if (
            !Number.isFinite(
                confidence
            )
        ) {

            confidence =
                Number(
                    source.confidence
                );
        }

        if (
            !Number.isFinite(
                confidence
            )
        ) {

            confidence = 0;
        }

        // ----------------------------------------------------
        // NORMALIZE 0-1
        // ----------------------------------------------------

        if (
            confidence > 1 &&
            confidence <= 100
        ) {

            confidence =
                confidence / 100;
        }

        confidence =
            Math.max(
                0,
                Math.min(
                    1,
                    confidence
                )
            );

        // ----------------------------------------------------
        // RISK SCORE
        // ----------------------------------------------------

        let riskScore =
            Number(
                classification.risk_score
            );

        if (
            !Number.isFinite(
                riskScore
            )
        ) {

            riskScore =
                Number(
                    source.risk_score
                );
        }

        if (
            !Number.isFinite(
                riskScore
            )
        ) {

            riskScore =
                Number(
                    classification.score
                );
        }

        if (
            !Number.isFinite(
                riskScore
            )
        ) {

            riskScore = 0;
        }

        if (
            riskScore > 1 &&
            riskScore <= 100
        ) {

            riskScore =
                riskScore / 100;
        }

        riskScore =
            Math.max(
                0,
                Math.min(
                    1,
                    riskScore
                )
            );

        // ----------------------------------------------------
        // EVIDENCE
        // ----------------------------------------------------

        const evidence =
            classification.evidence ||
            source.evidence ||
            null;

        // ----------------------------------------------------
        // RESULT
        // ----------------------------------------------------

        const parsed = {

            label:
                label || "UNKNOWN",

            confidence,

            riskScore,

            evidence
        };

        console.log(
            "[GUARDNET-AI] Parsed result:",
            parsed
        );

        return parsed;
    }

    // ========================================================
    // EVIDENCE FORMAT
    // ========================================================

    function buildEvidence(evidence) {

        if (
            !evidence ||
            typeof evidence !== "object"
        ) {

            return "";
        }

        const items = [];

        // ----------------------------------------------------
        // GAMBLING TERMS
        // ----------------------------------------------------

        const gambling =
            Array.isArray(
                evidence.gambling_terms
            )
                ? evidence.gambling_terms
                : [];

        if (
            gambling.length > 0
        ) {

            items.push(
                "Gambling: " +
                gambling
                    .slice(0, 6)
                    .join(", ")
            );
        }

        // ----------------------------------------------------
        // PROMOTIONAL TERMS
        // ----------------------------------------------------

        const promotional =
            Array.isArray(
                evidence.promotional_terms
            )
                ? evidence.promotional_terms
                : [];

        if (
            promotional.length > 0
        ) {

            items.push(
                "Promosi: " +
                promotional
                    .slice(0, 6)
                    .join(", ")
            );
        }

        // ----------------------------------------------------
        // STRONG PHRASES
        // ----------------------------------------------------

        const strong =
            Array.isArray(
                evidence.strong_promotional_phrases
            )
                ? evidence.strong_promotional_phrases
                : [];

        if (
            strong.length > 0
        ) {

            items.push(
                "Strong phrase: " +
                strong
                    .slice(0, 5)
                    .join(", ")
            );
        }

        // ----------------------------------------------------
        // ANTI GAMBLING
        // ----------------------------------------------------

        const anti =
            Array.isArray(
                evidence.anti_gambling_phrases
            )
                ? evidence.anti_gambling_phrases
                : [];

        if (
            anti.length > 0
        ) {

            items.push(
                "Anti-gambling: " +
                anti
                    .slice(0, 4)
                    .join(", ")
            );
        }

        // ----------------------------------------------------
        // CONTACT
        // ----------------------------------------------------

        const contact =
            Array.isArray(
                evidence.contact_evidence
            )
                ? evidence.contact_evidence
                : [];

        if (
            contact.length > 0
        ) {

            items.push(
                "Contact: " +
                contact
                    .slice(0, 4)
                    .join(", ")
            );
        }

        // ----------------------------------------------------
        // REASONS
        // ----------------------------------------------------

        const reasons =
            Array.isArray(
                evidence.reasons
            )
                ? evidence.reasons
                : [];

        if (
            reasons.length > 0
        ) {

            items.push(
                "Reason: " +
                reasons
                    .slice(0, 4)
                    .join(", ")
            );
        }

        if (
            items.length === 0
        ) {

            return "";
        }

        return `
            <div style="
                margin-top:10px;
                padding-top:9px;
                border-top:1px solid rgba(255,255,255,.15);
                font-size:11px;
                opacity:.92;
            ">

                <div style="
                    font-weight:700;
                    margin-bottom:5px;
                ">
                    Evidence
                </div>

                ${items
                    .map(
                        (item) =>
                            `
                            <div style="
                                margin:3px 0;
                            ">
                                • ${escapeHtml(item)}
                            </div>
                            `
                    )
                    .join("")}

            </div>
        `;
    }

    // ========================================================
    // HTML ESCAPE
    // ========================================================

    function escapeHtml(value) {

        return String(value)
            .replace(
                /&/g,
                "&amp;"
            )
            .replace(
                /</g,
                "&lt;"
            )
            .replace(
                />/g,
                "&gt;"
            )
            .replace(
                /"/g,
                "&quot;"
            )
            .replace(
                /'/g,
                "&#039;"
            );
    }

    // ========================================================
    // DISPLAY RESULT
    // ========================================================

    function displayResult(
        post,
        result
    ) {

        const oldBadge =
            post.querySelector(
                ".guardnet-ai-badge"
            );

        if (oldBadge) {
            oldBadge.remove();
        }

        const data =
            parseResult(result);

        const info =
            getLabelInfo(
                data.label
            );

        const badge =
            createBadge();

        const confidencePercent =
            Math.round(
                data.confidence * 100
            );

        const riskPercent =
            Math.round(
                data.riskScore * 100
            );

        badge.innerHTML = `

            <div style="
                font-size:16px;
                font-weight:700;
                margin-bottom:8px;
                letter-spacing:.5px;
            ">
                GUARDNET-AI
            </div>

            <div style="
                font-size:20px;
                font-weight:700;
                margin-bottom:5px;
            ">

                ${info.icon}

                ${escapeHtml(
                    data.label
                )}

                •

                ${escapeHtml(
                    info.title
                )}

            </div>

            <div style="
                font-size:12px;
                opacity:.9;
                margin-bottom:8px;
            ">
                ${escapeHtml(
                    info.description
                )}
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                gap:10px;
                font-size:12px;
                font-weight:700;
            ">

                <span>
                    Risk:
                    ${riskPercent}%
                </span>

                <span>
                    Confidence:
                    ${confidencePercent}%
                </span>

            </div>

            ${buildEvidence(
                data.evidence
            )}
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
    // DISPLAY ERROR
    // ========================================================

    function displayError(
        post,
        message = ""
    ) {

        const oldBadge =
            post.querySelector(
                ".guardnet-ai-badge"
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
                font-size:17px;
                font-weight:700;
                color:#ff7777;
            ">
                Backend Error
            </div>

            <div style="
                font-size:12px;
                margin-top:7px;
                opacity:.9;
            ">
                Pastikan backend aktif
                di 127.0.0.1:8000
            </div>

            ${
                message
                    ? `
                    <div style="
                        font-size:10px;
                        margin-top:8px;
                        opacity:.65;
                    ">
                        ${escapeHtml(
                            message
                        )}
                    </div>
                    `
                    : ""
            }

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
    // ANALYZE POST
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
            "%c[GUARDNET-AI] Menganalisis post:",
            "color:#00d9a5;font-weight:bold;",
            postKey
        );

        const content =
            extractPostContent(
                post
            );

        // ----------------------------------------------------
        // NO TEXT
        // ----------------------------------------------------

        if (
            !content.text
        ) {

            console.log(
                "[GUARDNET-AI] Tidak ada teks yang dapat dianalisis."
            );

            processedPosts.delete(
                postKey
            );

            return;
        }

        // ----------------------------------------------------
        // PAYLOAD
        // ----------------------------------------------------

        const payload = {

            text:
                content.text,

            caption:
                content.caption,

            comments:
                content.comments
        };

        console.log(
            "[GUARDNET-AI] Payload:",
            payload
        );

        console.log(
            "[GUARDNET-AI] Mengirim data ke backend..."
        );

        // ----------------------------------------------------
        // REQUEST
        // ----------------------------------------------------

        try {

            const response =
                await fetch(
                    BACKEND_URL,
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

            console.log(
                "[GUARDNET-AI] HTTP status:",
                response.status
            );

            // ------------------------------------------------
            // ERROR
            // ------------------------------------------------

            if (
                !response.ok
            ) {

                let errorBody =
                    "";

                try {

                    errorBody =
                        await response.text();

                } catch (_) {}

                console.error(
                    "[GUARDNET-AI] Backend error:",
                    response.status,
                    errorBody
                );

                throw new Error(
                    "HTTP " +
                    response.status
                );
            }

            // ------------------------------------------------
            // JSON
            // ------------------------------------------------

            const result =
                await response.json();

            console.log(
                "%c[GUARDNET-AI] BACKEND RESULT:",
                "color:#00d9a5;font-weight:bold;",
                result
            );

            // ------------------------------------------------
            // SAVE
            // ------------------------------------------------

            processedPosts.set(
                postKey,
                result
            );

            // ------------------------------------------------
            // DISPLAY
            // ------------------------------------------------

            displayResult(
                post,
                result
            );

        } catch (error) {

            console.error(
                "[GUARDNET-AI] Backend error:",
                error
            );

            processedPosts.set(
                postKey,
                "error"
            );

            displayError(
                post,
                error.message
            );
        }
    }

    // ========================================================
    // SCAN POSTS
    // ========================================================

    async function scanPosts() {

        if (scanRunning) {
            return;
        }

        scanRunning = true;

        try {

            const posts =
                getPosts();

            console.log(
                "[GUARDNET-AI] Visible posts:",
                posts.length
            );

            for (
                const post of posts
            ) {

                if (
                    !isVisible(
                        post
                    )
                ) {
                    continue;
                }

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

                await analyzePost(
                    post,
                    postKey
                );
            }

        } finally {

            scanRunning = false;
        }
    }

    // ========================================================
    // MUTATION OBSERVER
    // ========================================================

    const observer =
        new MutationObserver(
            () => {

                clearTimeout(
                    mutationTimer
                );

                mutationTimer =
                    setTimeout(
                        () => {

                            scanPosts();

                        },
                        MUTATION_DELAY
                    );
            }
        );

    function startObserver() {

        if (
            !document.body
        ) {

            setTimeout(
                startObserver,
                500
            );

            return;
        }

        observer.observe(
            document.body,
            {
                childList:
                    true,

                subtree:
                    true
            }
        );
    }

    startObserver();

    // ========================================================
    // SCROLL MONITOR
    // ========================================================

    window.addEventListener(
        "scroll",
        () => {

            clearTimeout(
                scrollTimer
            );

            scrollTimer =
                setTimeout(
                    () => {

                        console.log(
                            "[GUARDNET-AI] Scroll detected."
                        );

                        scanPosts();

                    },
                    SCROLL_DELAY
                );

        },
        {
            passive:
                true
        }
    );

    // ========================================================
    // PERIODIC MONITOR
    // ========================================================

    setInterval(
        () => {

            scanPosts();

        },
        SCAN_INTERVAL
    );

    // ========================================================
    // PAGE VISIBILITY
    // ========================================================

    document.addEventListener(
        "visibilitychange",
        () => {

            if (
                !document.hidden
            ) {

                setTimeout(
                    scanPosts,
                    500
                );
            }
        }
    );

    // ========================================================
    // START MONITORING
    // ========================================================

    setTimeout(
        () => {

            console.log(
                "%c[GUARDNET-AI] Real-time monitoring siap.",
                "color:#00d9a5;font-weight:bold;font-size:14px;"
            );

            scanPosts();

        },
        2000
    );

})();