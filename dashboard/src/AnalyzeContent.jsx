import React, { useMemo, useState } from "react";


// ============================================================
// GUARDNET-AI
// ANALYZE CONTENT PAGE
// ============================================================

const DEFAULT_API_BASE = "http://127.0.0.1:8000";


// ============================================================
// HELPERS
// ============================================================

function clamp(value, min = 0, max = 1) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return 0;
  }

  return Math.max(
    min,
    Math.min(max, number)
  );
}


function percent(value) {
  return `${(
    clamp(value) * 100
  ).toFixed(1)}%`;
}


function getRiskColor(label) {

  if (label === "C2") {
    return "#dc2626";
  }

  if (label === "C1") {
    return "#d97706";
  }

  return "#16a34a";
}


function getRiskBackground(label) {

  if (label === "C2") {
    return "#fef2f2";
  }

  if (label === "C1") {
    return "#fffbeb";
  }

  return "#f0fdf4";
}


function getRiskText(label) {

  if (label === "C2") {
    return "HIGH RISK";
  }

  if (label === "C1") {
    return "SUSPICIOUS";
  }

  return "NORMAL";
}


function safeArray(value) {

  return Array.isArray(value)
    ? value
    : [];

}


function safeObject(value) {

  if (
    value &&
    typeof value === "object" &&
    !Array.isArray(value)
  ) {
    return value;
  }

  return {};

}


// ============================================================
// MAIN COMPONENT
// ============================================================

export default function AnalyzeContent({
  apiBase = DEFAULT_API_BASE,
  onBack,
}) {

  // ==========================================================
  // STATE
  // ==========================================================

  const [file, setFile] = useState(null);

  const [previewUrl, setPreviewUrl] = useState("");

  const [caption, setCaption] = useState("");

  const [comments, setComments] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [result, setResult] = useState(null);


  // ==========================================================
  // FILE CHANGE
  // ==========================================================

  const handleFileChange = (event) => {

    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) {
      return;
    }


    const allowedTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];


    if (
      !allowedTypes.includes(
        selectedFile.type
      )
    ) {

      setError(
        "Format file tidak didukung. Gunakan JPG, JPEG, PNG, atau WEBP."
      );

      return;
    }


    if (
      selectedFile.size >
      10 * 1024 * 1024
    ) {

      setError(
        "Ukuran gambar maksimal 10 MB."
      );

      return;
    }


    setError("");

    setFile(selectedFile);

    setResult(null);


    const url =
      URL.createObjectURL(
        selectedFile
      );

    setPreviewUrl(url);

  };


  // ==========================================================
  // DRAG & DROP
  // ==========================================================

  const handleDrop = (event) => {

    event.preventDefault();

    const droppedFile =
      event.dataTransfer.files?.[0];

    if (!droppedFile) {
      return;
    }


    const allowedTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];


    if (
      !allowedTypes.includes(
        droppedFile.type
      )
    ) {

      setError(
        "Format file tidak didukung."
      );

      return;
    }


    if (
      droppedFile.size >
      10 * 1024 * 1024
    ) {

      setError(
        "Ukuran gambar maksimal 10 MB."
      );

      return;
    }


    setError("");

    setFile(droppedFile);

    setResult(null);


    const url =
      URL.createObjectURL(
        droppedFile
      );

    setPreviewUrl(url);

  };


  // ==========================================================
  // ANALYZE
  // ==========================================================

  const handleAnalyze = async () => {

    if (!file) {

      setError(
        "Silakan pilih gambar terlebih dahulu."
      );

      return;
    }


    setLoading(true);

    setError("");

    setResult(null);


    try {

      const formData =
        new FormData();


      // IMPORTANT:
      // Backend GuardNet-AI menerima field "image"
      formData.append(
        "image",
        file
      );


      // Optional fields
      formData.append(
        "caption",
        caption
      );


      formData.append(
        "comments",
        comments
      );


      const response =
        await fetch(
          `${apiBase}/api/analyze-image`,
          {
            method: "POST",
            body: formData,
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data?.detail
            ? JSON.stringify(
                data.detail
              )
            : data?.message ||
              "Analisis gagal."
        );

      }


      if (
        data?.status === "error"
      ) {

        throw new Error(
          data?.message ||
          data?.error ||
          "Backend mengembalikan error."
        );

      }


      setResult(data);

    } catch (err) {

      console.error(
        "GuardNet-AI analysis error:",
        err
      );


      setError(
        err?.message ||
        "Tidak dapat terhubung ke backend GuardNet-AI."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // RESET
  // ==========================================================

  const handleReset = () => {

    setFile(null);

    setPreviewUrl("");

    setCaption("");

    setComments("");

    setResult(null);

    setError("");

  };


  // ==========================================================
  // NORMALIZED RESULT
  // ==========================================================

  const normalized = useMemo(() => {

    if (!result) {
      return null;
    }


    const classification =
      safeObject(
        result.classification
      );


    const fusion =
      safeObject(
        result.fusion
      );


    const explanation =
      safeObject(
        classification.explanation
      );


    const visual =
      safeObject(
        result.visual
      );


    const ocr =
      safeObject(
        result.ocr
      );


    const entities =
      safeObject(
        result.entities
      );


    const payment =
      safeObject(
        result.payment
      );


    const qris =
      safeObject(
        result.qris
      );


    const digital =
      safeObject(
        result.digital_intelligence
      );


    const cyber =
      safeObject(
        result.cyber_security
      );


    const correlation =
      safeObject(
        result.cross_content_correlation ||
        result.correlation
      );


    const recurrence =
      safeObject(
        result.recurrence ||
        correlation.recurrence
      );


    const finalLabel =
      classification.classification ||
      classification.label ||
      fusion.classification ||
      "C0";


    const riskScore =
      classification.risk_score ??
      classification.score ??
      fusion.risk_score ??
      0;


    const confidence =
      classification.confidence ??
      fusion.confidence ??
      0;


    const adaptiveWeights =
      safeObject(
        classification.adaptive_weights ||
        fusion.adaptive_weights
      );


    const evidence =
      safeObject(
        classification.evidence ||
        fusion.evidence
      );


    return {

      classification,

      fusion,

      explanation,

      visual,

      ocr,

      entities,

      payment,

      qris,

      digital,

      cyber,

      correlation,

      recurrence,

      finalLabel,

      riskScore: clamp(
        riskScore
      ),

      confidence: clamp(
        confidence
      ),

      adaptiveWeights,

      evidence,

    };

  }, [result]);


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "34px",
        boxSizing: "border-box",
      }}
    >

      {/* ====================================================
          HEADER
          ==================================================== */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "28px",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >

        <div>

          {onBack && (

            <button
              type="button"
              onClick={onBack}
              style={backButtonStyle}
            >
              ← Dashboard
            </button>

          )}

          <div
            style={{
              color: "#6b7b98",
              fontSize: "13px",
              fontWeight: 700,
              marginTop: "10px",
            }}
          >
            GUARDNET-AI / ANALYSIS
          </div>


          <h1
            style={{
              margin:
                "8px 0 6px",
              fontSize: "34px",
              color: "#102448",
            }}
          >
            Analyze Content
          </h1>


          <p
            style={{
              margin: 0,
              color: "#70809b",
              fontSize: "15px",
            }}
          >
            Multimodal AI analysis for
            online gambling detection.
          </p>

        </div>


        {result && (

          <button
            type="button"
            onClick={handleReset}
            style={{
              border:
                "1px solid #d8e0ed",
              background: "#ffffff",
              color: "#20345b",
              borderRadius: "10px",
              padding:
                "11px 18px",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            New Analysis
          </button>

        )}

      </div>


      {/* ====================================================
          ERROR
          ==================================================== */}

      {error && (

        <div
          style={{
            background: "#fef2f2",
            border:
              "1px solid #fecaca",
            color: "#b91c1c",
            borderRadius: "12px",
            padding: "14px 18px",
            marginBottom: "20px",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          ⚠ {error}
        </div>

      )}


      {/* ====================================================
          INPUT AREA
          ==================================================== */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1.1fr) minmax(320px, 0.9fr)",
          gap: "22px",
          alignItems: "start",
        }}
      >


        {/* --------------------------------------------------
            IMAGE
            -------------------------------------------------- */}

        <div
          style={cardStyle}
        >

          <div
            style={{
              fontSize: "20px",
              fontWeight: 800,
              color: "#102448",
              marginBottom: "6px",
            }}
          >
            Multimodal Analysis
          </div>


          <div
            style={{
              color: "#7a89a3",
              fontSize: "14px",
              marginBottom: "18px",
            }}
          >
            Upload image untuk mendeteksi
            indikasi perjudian online.
          </div>


          {!previewUrl ? (

            <label
              onDragOver={(e) =>
                e.preventDefault()
              }
              onDrop={handleDrop}
              style={{
                minHeight: "320px",
                border:
                  "2px dashed #cbd8eb",
                borderRadius: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                cursor: "pointer",
                background: "#f8faff",
                textAlign: "center",
              }}
            >

              <div
                style={{
                  width: "56px",
                  height: "56px",
                  borderRadius: "16px",
                  background: "#eaf1ff",
                  color: "#2563eb",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "26px",
                  marginBottom: "14px",
                }}
              >
                ↑
              </div>


              <strong
                style={{
                  color: "#17335e",
                  fontSize: "17px",
                }}
              >
                Upload image
              </strong>


              <span
                style={{
                  color: "#8a99b2",
                  fontSize: "13px",
                  marginTop: "6px",
                }}
              >
                JPG, JPEG, PNG, WEBP
              </span>


              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={
                  handleFileChange
                }
                style={{
                  display: "none",
                }}
              />

            </label>

          ) : (

            <div>

              <div
                style={{
                  borderRadius: "16px",
                  overflow: "hidden",
                  border:
                    "1px solid #dbe3ef",
                  background: "#f8fafc",
                  maxHeight: "520px",
                  display: "flex",
                  justifyContent:
                    "center",
                }}
              >

                <img
                  src={previewUrl}
                  alt="Preview"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "520px",
                    objectFit: "contain",
                  }}
                />

              </div>


              <div
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  alignItems: "center",
                  marginTop: "12px",
                  gap: "10px",
                }}
              >

                <div
                  style={{
                    fontSize: "13px",
                    color: "#63738f",
                    overflow: "hidden",
                    textOverflow:
                      "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {file?.name}
                </div>


                <button
                  type="button"
                  onClick={() => {

                    setFile(null);

                    setPreviewUrl("");

                    setResult(null);

                  }}
                  style={{
                    border: "none",
                    background:
                      "#fef2f2",
                    color: "#dc2626",
                    borderRadius: "8px",
                    padding:
                      "7px 11px",
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  Remove
                </button>

              </div>

            </div>

          )}

        </div>


        {/* --------------------------------------------------
            TEXT INPUT
            -------------------------------------------------- */}

        <div
          style={cardStyle}
        >

          <div
            style={{
              fontSize: "20px",
              fontWeight: 800,
              color: "#102448",
              marginBottom: "6px",
            }}
          >
            Text Intelligence
          </div>


          <div
            style={{
              color: "#7a89a3",
              fontSize: "14px",
              marginBottom: "18px",
            }}
          >
            Tambahkan caption dan komentar
            untuk memperkuat analisis.
          </div>


          <label
            style={labelStyle}
          >
            Caption Instagram
          </label>


          <textarea
            value={caption}
            onChange={(e) =>
              setCaption(e.target.value)
            }
            placeholder="Masukkan caption Instagram..."
            style={{
              ...inputStyle,
              minHeight: "90px",
              resize: "vertical",
            }}
          />


          <label
            style={{
              ...labelStyle,
              marginTop: "16px",
            }}
          >
            Comments
          </label>


          <textarea
            value={comments}
            onChange={(e) =>
              setComments(e.target.value)
            }
            placeholder={
              "Satu komentar per baris...\ncontoh: gampang scatter bosku"
            }
            style={{
              ...inputStyle,
              minHeight: "120px",
              resize: "vertical",
            }}
          />


          <button
            type="button"
            disabled={
              loading || !file
            }
            onClick={
              handleAnalyze
            }
            style={{
              width: "100%",
              marginTop: "20px",
              border: "none",
              borderRadius: "11px",
              padding: "14px",
              background:
                loading || !file
                  ? "#a9c1f7"
                  : "#2563eb",
              color: "#ffffff",
              fontSize: "15px",
              fontWeight: 800,
              cursor:
                loading || !file
                  ? "not-allowed"
                  : "pointer",
            }}
          >
            {loading
              ? "Analyzing GuardNet-AI..."
              : "Analyze Content"}
          </button>

        </div>

      </div>


      {/* ====================================================
          RESULT
          ==================================================== */}

      {normalized && (

        <div
          style={{
            marginTop: "24px",
          }}
        >


          {/* ==================================================
              FINAL CLASSIFICATION
              ================================================== */}

          <div
            style={{
              ...cardStyle,
              background:
                getRiskBackground(
                  normalized.finalLabel
                ),
              border:
                `1px solid ${getRiskColor(
                  normalized.finalLabel
                )}33`,
            }}
          >

            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                alignItems: "center",
                gap: "20px",
                flexWrap: "wrap",
              }}
            >

              <div>

                <div
                  style={{
                    fontSize: "13px",
                    color: "#71819b",
                    fontWeight: 800,
                    letterSpacing:
                      "0.05em",
                  }}
                >
                  FINAL CLASSIFICATION
                </div>


                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                    marginTop: "8px",
                  }}
                >

                  <span
                    style={{
                      fontSize: "40px",
                      fontWeight: 900,
                      color:
                        getRiskColor(
                          normalized.finalLabel
                        ),
                    }}
                  >
                    {normalized.finalLabel}
                  </span>


                  <span
                    style={{
                      color:
                        getRiskColor(
                          normalized.finalLabel
                        ),
                      fontWeight: 800,
                      fontSize: "17px",
                    }}
                  >
                    {getRiskText(
                      normalized.finalLabel
                    )}
                  </span>

                </div>

              </div>


              <div
                style={{
                  display: "flex",
                  gap: "34px",
                }}
              >

                <Metric
                  title="Risk Score"
                  value={percent(
                    normalized.riskScore
                  )}
                />


                <Metric
                  title="Confidence"
                  value={percent(
                    normalized.confidence
                  )}
                />

              </div>

            </div>

          </div>


          {/* ==================================================
              MODALITIES
              ================================================== */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(5, minmax(0, 1fr))",
              gap: "14px",
              marginTop: "20px",
            }}
          >

            <ModalityCard
              name="Text"
              active={
                safeArray(
                  normalized.classification
                    ?.active_modality_names
                ).includes("text")
              }
            />


            <ModalityCard
              name="OCR"
              active={
                safeArray(
                  normalized.classification
                    ?.active_modality_names
                ).includes("ocr")
              }
            />


            <ModalityCard
              name="Visual"
              active={
                safeArray(
                  normalized.classification
                    ?.active_modality_names
                ).includes("visual")
              }
            />


            <ModalityCard
              name="Payment"
              active={
                safeArray(
                  normalized.classification
                    ?.active_modality_names
                ).includes("payment")
              }
            />


            <ModalityCard
              name="Entity"
              active={
                safeArray(
                  normalized.classification
                    ?.active_modality_names
                ).includes("entity")
              }
            />

          </div>


          {/* ==================================================
              EVIDENCE + EXPLANATION
              ================================================== */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "minmax(0, 1fr) minmax(0, 1fr)",
              gap: "20px",
              marginTop: "20px",
            }}
          >

            {/* EXPLAINABLE AI */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Explainable AI
              </SectionTitle>


              <div
                style={{
                  background:
                    "#f8faff",
                  borderRadius: "12px",
                  padding: "16px",
                  color: "#344563",
                  lineHeight: 1.7,
                  fontSize: "14px",
                }}
              >

                {normalized.explanation
                  ?.summary ||
                  "Tidak tersedia ringkasan penjelasan."}

              </div>


              <div
                style={{
                  marginTop: "16px",
                }}
              >

                <strong
                  style={{
                    color: "#1b3157",
                    fontSize: "14px",
                  }}
                >
                  Reasons
                </strong>


                <ul
                  style={{
                    marginTop: "10px",
                    paddingLeft: "20px",
                    color: "#566783",
                    lineHeight: 1.7,
                  }}
                >

                  {safeArray(
                    normalized.explanation
                      ?.reasons
                  ).length > 0 ? (

                    safeArray(
                      normalized.explanation
                        ?.reasons
                    ).map(
                      (reason, index) => (

                        <li
                          key={index}
                        >
                          {reason}
                        </li>

                      )
                    )

                  ) : (

                    <li>
                      Tidak terdapat
                      evidence kuat.
                    </li>

                  )}

                </ul>

              </div>

            </section>


            {/* EVIDENCE */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Detection Evidence
              </SectionTitle>


              <EvidenceList
                title="Gambling Terms"
                items={
                  normalized.ocr
                    ?.gambling_terms ||
                  normalized.evidence
                    ?.ocr
                    ?.gambling_terms
                }
              />


              <EvidenceList
                title="Promotional Evidence"
                items={
                  normalized.ocr
                    ?.strong_promotional_phrases ||
                  normalized.evidence
                    ?.cross_modal
                    ?.promotional_hits
                }
              />


              <EvidenceList
                title="Visual Evidence"
                items={
                  normalized.visual
                    ?.evidence
                }
              />

            </section>

          </div>


          {/* ==================================================
              ADAPTIVE WEIGHTS
              ================================================== */}

          <section
            style={{
              ...cardStyle,
              marginTop: "20px",
            }}
          >

            <SectionTitle>
              Multimodal Adaptive Weights
            </SectionTitle>


            <p
              style={{
                color: "#75849e",
                fontSize: "14px",
                marginTop: 0,
              }}
            >
              Bobot modalitas yang digunakan
              dalam proses multimodal fusion.
            </p>


            <div
              style={{
                display: "grid",
                gap: "13px",
              }}
            >

              <WeightBar
                name="Text"
                value={
                  normalized.adaptiveWeights
                    ?.text || 0
                }
              />


              <WeightBar
                name="OCR"
                value={
                  normalized.adaptiveWeights
                    ?.ocr || 0
                }
              />


              <WeightBar
                name="Visual"
                value={
                  normalized.adaptiveWeights
                    ?.visual || 0
                }
              />


              <WeightBar
                name="Payment"
                value={
                  normalized.adaptiveWeights
                    ?.payment || 0
                }
              />


              <WeightBar
                name="Entity"
                value={
                  normalized.adaptiveWeights
                    ?.entity || 0
                }
              />

            </div>

          </section>


          {/* ==================================================
              INTELLIGENCE GRID
              ================================================== */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(3, minmax(0, 1fr))",
              gap: "20px",
              marginTop: "20px",
            }}
          >

            {/* OCR */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                OCR Intelligence
              </SectionTitle>


              <InfoRow
                label="Status"
                value={
                  normalized.ocr
                    ?.status ||
                  "unknown"
                }
              />


              <InfoRow
                label="Quality"
                value={
                  normalized.ocr
                    ?.quality != null
                    ? percent(
                        normalized.ocr
                          .quality
                      )
                    : "-"
                }
              />


              <InfoRow
                label="Variants"
                value={
                  normalized.ocr
                    ?.variants_tested ??
                  "-"
                }
              />


              <div
                style={{
                  marginTop: "14px",
                  maxHeight: "180px",
                  overflow: "auto",
                  background:
                    "#f8fafc",
                  borderRadius: "9px",
                  padding: "12px",
                  fontSize: "12px",
                  color: "#5b6b86",
                  whiteSpace:
                    "pre-wrap",
                }}
              >
                {normalized.ocr
                  ?.text ||
                  "Tidak ada OCR text."}
              </div>

            </section>


            {/* VISUAL */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Visual Intelligence
              </SectionTitle>


              <InfoRow
                label="Visual Score"
                value={
                  percent(
                    normalized.visual
                      ?.visual_score || 0
                  )
                }
              />


              <InfoRow
                label="Brightness"
                value={
                  normalized.visual
                    ?.brightness ??
                  "-"
                }
              />


              <InfoRow
                label="Contrast"
                value={
                  normalized.visual
                    ?.contrast ??
                  "-"
                }
              />


              <InfoRow
                label="Saturation"
                value={
                  normalized.visual
                    ?.saturation ??
                  "-"
                }
              />


              <InfoRow
                label="Text Density"
                value={
                  normalized.visual
                    ?.text_density ??
                  "-"
                }
              />

            </section>


            {/* ENTITY */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Entity Intelligence
              </SectionTitle>


              <InfoRow
                label="Accounts"
                value={
                  safeArray(
                    normalized.entities
                      ?.account
                  ).length
                }
              />


              <InfoRow
                label="Phone"
                value={
                  safeArray(
                    normalized.entities
                      ?.phone
                  ).length
                }
              />


              <InfoRow
                label="URLs"
                value={
                  safeArray(
                    normalized.entities
                      ?.url
                  ).length
                }
              />


              <InfoRow
                label="Domains"
                value={
                  safeArray(
                    normalized.entities
                      ?.domain
                  ).length
                }
              />


              <InfoRow
                label="Entity Count"
                value={
                  normalized.entities
                    ?.entity_count ??
                  0
                }
              />

            </section>

          </div>


          {/* ==================================================
              PAYMENT + CYBER SECURITY
              ================================================== */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "minmax(0, 1fr) minmax(0, 1fr)",
              gap: "20px",
              marginTop: "20px",
            }}
          >

            {/* PAYMENT */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Payment Intelligence
              </SectionTitle>


              <InfoRow
                label="Payment Detected"
                value={
                  normalized.payment
                    ?.detected
                    ? "YES"
                    : "NO"
                }
              />


              <InfoRow
                label="Payment Risk"
                value={
                  percent(
                    normalized.payment
                      ?.risk || 0
                  )
                }
              />


              <InfoRow
                label="QRIS"
                value={
                  normalized.qris
                    ?.detected
                    ? "DETECTED"
                    : "NOT DETECTED"
                }
              />


              {normalized.qris
                ?.merchant_name && (

                <InfoRow
                  label="Merchant"
                  value={
                    normalized.qris
                      .merchant_name
                  }
                />

              )}

            </section>


            {/* CYBER SECURITY */}

            <section
              style={cardStyle}
            >

              <SectionTitle>
                Cyber Security Layer
              </SectionTitle>


              <InfoRow
                label="Security Score"
                value={
                  percent(
                    normalized.cyber
                      ?.security_score ??
                    normalized.riskScore
                  )
                }
              />


              <InfoRow
                label="Severity"
                value={
                  normalized.cyber
                    ?.severity ||
                  getRiskText(
                    normalized.finalLabel
                  )
                }
              />


              <InfoRow
                label="Action"
                value={
                  normalized.cyber
                    ?.action ||
                  "-"
                }
              />


              <div
                style={{
                  marginTop: "15px",
                }}
              >

                <strong
                  style={{
                    color: "#1b3157",
                    fontSize: "14px",
                  }}
                >
                  Security Alerts
                </strong>


                <ul
                  style={{
                    marginTop: "8px",
                    paddingLeft: "20px",
                    color: "#5a6b86",
                    lineHeight: 1.6,
                    fontSize: "13px",
                  }}
                >

                  {safeArray(
                    normalized.cyber
                      ?.alerts
                  ).length > 0 ? (

                    safeArray(
                      normalized.cyber
                        ?.alerts
                    ).map(
                      (alert, index) => (

                        <li
                          key={index}
                        >
                          {alert}
                        </li>

                      )
                    )

                  ) : (

                    <li>
                      No critical
                      cyber-security
                      indicator detected.
                    </li>

                  )}

                </ul>

              </div>

            </section>

          </div>


          {/* ==================================================
              CYBER INTELLIGENCE
              ================================================== */}

          <section
            style={{
              ...cardStyle,
              marginTop: "20px",
            }}
          >

            <SectionTitle>
              Cyber Intelligence & Correlation
            </SectionTitle>


            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(6, minmax(0, 1fr))",
                gap: "12px",
              }}
            >

              <SmallStat
                title="Accounts"
                value={
                  safeArray(
                    normalized.digital
                      ?.account
                  ).length
                }
              />


              <SmallStat
                title="Domains"
                value={
                  safeArray(
                    normalized.digital
                      ?.domain
                  ).length
                }
              />


              <SmallStat
                title="URLs"
                value={
                  safeArray(
                    normalized.digital
                      ?.url
                  ).length
                }
              />


              <SmallStat
                title="Contacts"
                value={
                  safeArray(
                    normalized.digital
                      ?.contact
                  ).length
                }
              />


              <SmallStat
                title="Related Cases"
                value={
                  normalized.correlation
                    ?.related_case_count ??
                  0
                }
              />


              <SmallStat
                title="Shared Indicators"
                value={
                  normalized.correlation
                    ?.shared_indicator_count ??
                  0
                }
              />

            </div>


            <div
              style={{
                display: "flex",
                gap: "20px",
                flexWrap: "wrap",
                marginTop: "18px",
              }}
            >

              <InfoRow
                label="Correlation Level"
                value={
                  normalized.correlation
                    ?.correlation_level ||
                  "NONE"
                }
              />


              <InfoRow
                label="Recurrence Level"
                value={
                  normalized.recurrence
                    ?.level ||
                  "NONE"
                }
              />


              <InfoRow
                label="Recurrence Count"
                value={
                  normalized.recurrence
                    ?.count ??
                  0
                }
              />

            </div>

          </section>


          {/* ==================================================
              RAW COMBINED TEXT
              ================================================== */}

          <section
            style={{
              ...cardStyle,
              marginTop: "20px",
            }}
          >

            <SectionTitle>
              Extracted Content
            </SectionTitle>


            <div
              style={{
                background:
                  "#0f172a",
                color:
                  "#dbeafe",
                borderRadius:
                  "12px",
                padding:
                  "16px",
                maxHeight:
                  "300px",
                overflow:
                  "auto",
                whiteSpace:
                  "pre-wrap",
                fontSize:
                  "12px",
                lineHeight:
                  1.65,
                fontFamily:
                  "Consolas, monospace",
              }}
            >
              {result?.combined_text ||
                result?.text?.text ||
                result?.ocr?.text ||
                "Tidak terdapat text hasil ekstraksi."}
            </div>

          </section>

        </div>

      )}

    </div>

  );

}


// ============================================================
// COMPONENTS
// ============================================================

function Metric({
  title,
  value,
}) {

  return (

    <div>

      <div
        style={{
          color: "#73829d",
          fontSize: "12px",
          fontWeight: 700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          color: "#132a50",
          fontSize: "24px",
          fontWeight: 900,
          marginTop: "3px",
        }}
      >
        {value}
      </div>

    </div>

  );

}


function SectionTitle({
  children,
}) {

  return (

    <h2
      style={{
        margin:
          "0 0 16px",
        color: "#102448",
        fontSize: "18px",
        fontWeight: 850,
      }}
    >
      {children}
    </h2>

  );

}


function ModalityCard({
  name,
  active,
}) {

  return (

    <div
      style={{
        background:
          active
            ? "#eff6ff"
            : "#f8fafc",
        border:
          `1px solid ${
            active
              ? "#bfdbfe"
              : "#e2e8f0"
          }`,
        borderRadius:
          "12px",
        padding:
          "14px",
        display:
          "flex",
        alignItems:
          "center",
        gap:
          "9px",
      }}
    >

      <span
        style={{
          width: "10px",
          height: "10px",
          borderRadius:
            "50%",
          background:
            active
              ? "#2563eb"
              : "#cbd5e1",
        }}
      />

      <span
        style={{
          fontSize:
            "13px",
          fontWeight:
            750,
          color:
            active
              ? "#1d4ed8"
              : "#7a879c",
        }}
      >
        {name}
      </span>


      <span
        style={{
          marginLeft:
            "auto",
          fontSize:
            "12px",
          fontWeight:
            700,
          color:
            active
              ? "#2563eb"
              : "#94a3b8",
        }}
      >
        {active
          ? "ACTIVE"
          : "OFF"}
      </span>

    </div>

  );

}


function EvidenceList({
  title,
  items,
}) {

  const safeItems =
    safeArray(items);


  return (

    <div
      style={{
        marginBottom:
          "15px",
      }}
    >

      <div
        style={{
          color: "#314564",
          fontWeight: 750,
          fontSize: "13px",
          marginBottom:
            "8px",
        }}
      >
        {title}
      </div>


      {safeItems.length > 0 ? (

        <div
          style={{
            display:
              "flex",
            gap:
              "7px",
            flexWrap:
              "wrap",
          }}
        >

          {safeItems.map(
            (item, index) => (

              <span
                key={index}
                style={{
                  background:
                    "#eef4ff",
                  color:
                    "#2458b9",
                  borderRadius:
                    "7px",
                  padding:
                    "6px 9px",
                  fontSize:
                    "12px",
                  fontWeight:
                    700,
                }}
              >
                {String(item)}
              </span>

            )
          )}

        </div>

      ) : (

        <span
          style={{
            color:
              "#9aa6b8",
            fontSize:
              "12px",
          }}
        >
          Tidak ada evidence.
        </span>

      )}

    </div>

  );

}


function WeightBar({
  name,
  value,
}) {

  const normalizedValue =
    clamp(value);


  return (

    <div>

      <div
        style={{
          display:
            "flex",
          justifyContent:
            "space-between",
          marginBottom:
            "6px",
          fontSize:
            "13px",
          fontWeight:
            700,
          color:
            "#455675",
        }}
      >

        <span>
          {name}
        </span>

        <span>
          {percent(
            normalizedValue
          )}
        </span>

      </div>


      <div
        style={{
          height:
            "9px",
          background:
            "#e7edf6",
          borderRadius:
            "999px",
          overflow:
            "hidden",
        }}
      >

        <div
          style={{
            width:
              `${normalizedValue * 100}%`,
            height:
              "100%",
            background:
              "#2563eb",
            borderRadius:
              "999px",
            transition:
              "width 0.4s ease",
          }}
        />

      </div>

    </div>

  );

}


function InfoRow({
  label,
  value,
}) {

  return (

    <div
      style={{
        display:
          "flex",
        justifyContent:
          "space-between",
        gap:
          "15px",
        padding:
          "8px 0",
        borderBottom:
          "1px solid #edf1f6",
        fontSize:
          "13px",
      }}
    >

      <span
        style={{
          color:
            "#78879f",
        }}
      >
        {label}
      </span>

      <strong
        style={{
          color:
            "#263b5d",
          textAlign:
            "right",
          wordBreak:
            "break-word",
        }}
      >
        {String(
          value ?? "-"
        )}
      </strong>

    </div>

  );

}


function SmallStat({
  title,
  value,
}) {

  return (

    <div
      style={{
        background:
          "#f8fafc",
        border:
          "1px solid #e4eaf3",
        borderRadius:
          "11px",
        padding:
          "14px",
      }}
    >

      <div
        style={{
          color:
            "#78879f",
          fontSize:
            "12px",
          fontWeight:
            700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          color:
            "#16325e",
          fontSize:
            "22px",
          fontWeight:
            900,
          marginTop:
            "5px",
        }}
      >
        {value}
      </div>

    </div>

  );

}


// ============================================================
// STYLES
// ============================================================

const cardStyle = {
  background:
    "#ffffff",
  border:
    "1px solid #e0e7f1",
  borderRadius:
    "16px",
  padding:
    "22px",
  boxShadow:
    "0 5px 18px rgba(20, 40, 80, 0.04)",
  boxSizing:
    "border-box",
};


const inputStyle = {
  width:
    "100%",
  boxSizing:
    "border-box",
  border:
    "1px solid #d8e1ee",
  borderRadius:
    "10px",
  padding:
    "12px 14px",
  fontSize:
    "14px",
  color:
    "#243858",
  outline:
    "none",
  background:
    "#ffffff",
  fontFamily:
    "inherit",
};


const labelStyle = {
  display:
    "block",
  color:
    "#435674",
  fontSize:
    "13px",
  fontWeight:
    750,
  marginBottom:
    "7px",
};


const backButtonStyle = {
  border:
    "none",
  background:
    "transparent",
  padding:
    0,
  color:
    "#2563eb",
  fontSize:
    "13px",
  fontWeight:
    800,
  cursor:
    "pointer",
};