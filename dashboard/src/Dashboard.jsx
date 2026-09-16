import React, { useEffect, useMemo, useRef, useState } from "react";

function Dashboard({ apiBase, onOpenCases }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const [textInput, setTextInput] = useState("");
  const [captionInput, setCaptionInput] = useState("");
  const [commentsInput, setCommentsInput] = useState("");

  const fileInputRef = useRef(null);

  // =========================================================
  // HELPERS
  // =========================================================

  const normalizeArray = (value) => {
    if (Array.isArray(value)) return value;
    if (!value) return [];
    return [value];
  };

  const getClassification = (item) => {
    const classification =
      item?.classification ||
      item?.fusion?.classification ||
      item?.classification?.classification;

    if (typeof classification === "string") {
      return classification;
    }

    return (
      item?.classification?.classification ||
      "C0"
    );
  };

  const getRiskScore = (item) => {
    const value =
      item?.risk_score ??
      item?.classification?.risk_score ??
      item?.fusion?.risk_score ??
      0;

    const number = Number(value);

    return Number.isFinite(number)
      ? number
      : 0;
  };

  const getConfidence = (item) => {
    const value =
      item?.confidence ??
      item?.classification?.confidence ??
      item?.fusion?.confidence ??
      0;

    const number = Number(value);

    return Number.isFinite(number)
      ? number
      : 0;
  };

  const classificationText = (classification) => {
    if (classification === "C2") {
      return "HIGH RISK";
    }

    if (classification === "C1") {
      return "SUSPICIOUS";
    }

    return "LOW RISK";
  };

  // =========================================================
  // LOAD CASES
  // =========================================================

  const loadCases = async () => {
    setLoading(true);

    try {
      const possibleEndpoints = [
        "/api/cases",
        "/cases",
        "/api/dashboard/cases",
      ];

      let result = null;

      for (const endpoint of possibleEndpoints) {
        try {
          const response = await fetch(
            `${apiBase}${endpoint}`
          );

          if (!response.ok) {
            continue;
          }

          const data = await response.json();

          if (Array.isArray(data)) {
            result = data;
            break;
          }

          if (Array.isArray(data?.cases)) {
            result = data.cases;
            break;
          }

          if (Array.isArray(data?.items)) {
            result = data.items;
            break;
          }
        } catch (error) {
          // try next endpoint
        }
      }

      setCases(result || []);
      setBackendOnline(true);
    } catch (error) {
      console.error("Failed loading cases:", error);
      setCases([]);
      setBackendOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();

    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, []);

  // =========================================================
  // STATISTICS
  // =========================================================

  const statistics = useMemo(() => {
    const total = cases.length;

    const c0 = cases.filter(
      (item) => getClassification(item) === "C0"
    ).length;

    const c1 = cases.filter(
      (item) => getClassification(item) === "C1"
    ).length;

    const c2 = cases.filter(
      (item) => getClassification(item) === "C2"
    ).length;

    const highPriority = cases.filter((item) => {
      const risk = getRiskScore(item);

      return (
        getClassification(item) === "C2" ||
        risk >= 0.75
      );
    }).length;

    const pendingReview = cases.filter((item) => {
      const security =
        item?.cyber_security ||
        item?.cyberSecurity ||
        {};

      return (
        security?.severity === "HIGH" ||
        security?.severity === "MEDIUM" ||
        item?.status === "PENDING_REVIEW" ||
        getClassification(item) === "C2"
      );
    }).length;

    return {
      total,
      c0,
      c1,
      c2,
      highPriority,
      pendingReview,
    };
  }, [cases]);

  // =========================================================
  // IMAGE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const url = URL.createObjectURL(file);

    setPreviewUrl(url);
    setAnalysisResult(null);
  };

  // =========================================================
  // IMAGE ANALYSIS
  // =========================================================

  const analyzeImage = async () => {
    if (!selectedFile) {
      alert("Pilih gambar terlebih dahulu.");
      return;
    }

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const formData = new FormData();

      // Backend kamu menggunakan field "image"
      formData.append(
        "image",
        selectedFile
      );

      const response = await fetch(
        `${apiBase}/api/analyze-image`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail
            ? JSON.stringify(data.detail)
            : "Image analysis failed"
        );
      }

      setAnalysisResult(data);

      await loadCases();
    } catch (error) {
      console.error(error);

      setAnalysisResult({
        status: "error",
        error: error.message,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // =========================================================
  // TEXT ANALYSIS
  // =========================================================

  const analyzeText = async () => {
    if (!textInput.trim() && !captionInput.trim()) {
      alert(
        "Masukkan teks atau caption terlebih dahulu."
      );
      return;
    }

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const comments = commentsInput
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean);

      const payload = {
        text: textInput,
        caption: captionInput,
        comments,
      };

      const response = await fetch(
        `${apiBase}/api/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail
            ? JSON.stringify(data.detail)
            : "Text analysis failed"
        );
      }

      setAnalysisResult(data);

      await loadCases();
    } catch (error) {
      console.error(error);

      setAnalysisResult({
        status: "error",
        error: error.message,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // =========================================================
  // RESULT DATA
  // =========================================================

  const resultClassification =
    analysisResult
      ? getClassification(
          analysisResult
        )
      : null;

  const resultRisk =
    analysisResult
      ? getRiskScore(
          analysisResult
        )
      : 0;

  const resultConfidence =
    analysisResult
      ? getConfidence(
          analysisResult
        )
      : 0;

  const explanation =
    analysisResult?.classification
      ?.explanation ||
    analysisResult?.fusion
      ?.explanation ||
    analysisResult?.explanation ||
    null;

  const cyberSecurity =
    analysisResult?.cyber_security ||
    analysisResult?.classification
      ?.cyber_security ||
    null;

  const digitalIntelligence =
    analysisResult?.digital_intelligence ||
    null;

  const correlation =
    analysisResult?.cross_content_correlation ||
    analysisResult?.correlation ||
    null;

  const activeModalities =
    analysisResult?.classification
      ?.active_modality_names ||
    analysisResult?.fusion
      ?.active_modality_names ||
    [];

  const evidence =
    analysisResult?.classification
      ?.evidence ||
    analysisResult?.fusion?.evidence ||
    {};

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="dashboard-page">

      {/* HEADER */}
      <header className="page-header">
        <div>
          <div className="breadcrumb">
            GUARDNET-AI
            <span>/</span>
            Dashboard
          </div>

          <h1>
            Security Dashboard
          </h1>

          <p>
            GuardNet-AI multimodal
            threat detection
          </p>
        </div>

        <div className="header-actions">
          <div className="live-indicator">
            <span
              className={`status-dot ${
                backendOnline
                  ? "green"
                  : "red"
              }`}
            />

            {backendOnline
              ? "LIVE"
              : "OFFLINE"}
          </div>

          <button
            className="refresh-button"
            onClick={loadCases}
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* STATISTICS */}
      <section className="stats-grid">

        <div className="stat-card">
          <div className="stat-icon blue">
            ▣
          </div>

          <div>
            <div className="stat-label">
              Total Cases
            </div>

            <div className="stat-value">
              {loading
                ? "..."
                : statistics.total}
            </div>

            <div className="stat-description">
              All detected cases
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon red">
            ⚠
          </div>

          <div>
            <div className="stat-label">
              C2 Promotions
            </div>

            <div className="stat-value">
              {loading
                ? "..."
                : statistics.c2}
            </div>

            <div className="stat-description">
              High-risk gambling promotion
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon yellow">
            !
          </div>

          <div>
            <div className="stat-label">
              High Priority
            </div>

            <div className="stat-value">
              {loading
                ? "..."
                : statistics.highPriority}
            </div>

            <div className="stat-description">
              Requires immediate review
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple">
            ◷
          </div>

          <div>
            <div className="stat-label">
              Pending Review
            </div>

            <div className="stat-value">
              {loading
                ? "..."
                : statistics.pendingReview}
            </div>

            <div className="stat-description">
              Awaiting human verification
            </div>
          </div>
        </div>

      </section>

      {/* CLASSIFICATION SUMMARY */}
      <section className="classification-grid">

        <div className="classification-card">
          <div>
            <span className="classification-dot c0" />
            C0 — Normal
          </div>

          <strong>
            {statistics.c0}
          </strong>
        </div>

        <div className="classification-card">
          <div>
            <span className="classification-dot c1" />
            C1 — Suspicious
          </div>

          <strong>
            {statistics.c1}
          </strong>
        </div>

        <div className="classification-card">
          <div>
            <span className="classification-dot c2" />
            C2 — High Risk
          </div>

          <strong>
            {statistics.c2}
          </strong>
        </div>

      </section>

      {/* ANALYSIS AREA */}
      <section className="analysis-grid">

        {/* IMAGE ANALYSIS */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Multimodal Analysis
              </h2>

              <p>
                Upload image untuk
                mendeteksi indikasi
                perjudian online.
              </p>
            </div>
          </div>

          <div
            className="upload-area"
            onClick={() =>
              fileInputRef.current?.click()
            }
          >
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Preview"
                className="image-preview"
              />
            ) : (
              <>
                <div className="upload-icon">
                  ↑
                </div>

                <strong>
                  Upload image
                </strong>

                <span>
                  JPG, JPEG, PNG
                </span>
              </>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{
              display: "none",
            }}
          />

          {selectedFile && (
            <div className="selected-file">
              <span>
                {selectedFile.name}
              </span>

              <button
                onClick={() =>
                  setSelectedFile(null)
                }
              >
                ×
              </button>
            </div>
          )}

          <button
            className="primary-button"
            onClick={analyzeImage}
            disabled={
              analyzing ||
              !selectedFile
            }
          >
            {analyzing
              ? "Analyzing..."
              : "Analyze Image"}
          </button>
        </div>

        {/* TEXT ANALYSIS */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Text Intelligence
              </h2>

              <p>
                Analisis caption, teks,
                dan komentar.
              </p>
            </div>
          </div>

          <textarea
            className="input-area"
            placeholder="Masukkan teks konten..."
            value={textInput}
            onChange={(e) =>
              setTextInput(e.target.value)
            }
          />

          <input
            className="text-input"
            placeholder="Caption Instagram..."
            value={captionInput}
            onChange={(e) =>
              setCaptionInput(
                e.target.value
              )
            }
          />

          <textarea
            className="input-area small"
            placeholder="Komentar, satu komentar per baris..."
            value={commentsInput}
            onChange={(e) =>
              setCommentsInput(
                e.target.value
              )
            }
          />

          <button
            className="secondary-button"
            onClick={analyzeText}
            disabled={analyzing}
          >
            {analyzing
              ? "Analyzing..."
              : "Analyze Text"}
          </button>
        </div>

      </section>

      {/* RESULT */}
      {analysisResult && (
        <section className="result-panel">

          <div className="result-header">
            <div>
              <div className="result-overline">
                AI ANALYSIS RESULT
              </div>

              <h2>
                Detection Result
              </h2>
            </div>

            {resultClassification && (
              <div
                className={`classification-badge ${resultClassification.toLowerCase()}`}
              >
                {resultClassification}
                <span>
                  {classificationText(
                    resultClassification
                  )}
                </span>
              </div>
            )}
          </div>

          {analysisResult.status ===
          "error" ? (
            <div className="error-box">
              <strong>
                Analysis Error
              </strong>

              <p>
                {analysisResult.error}
              </p>
            </div>
          ) : (
            <>
              <div className="result-metrics">

                <div className="metric">
                  <span>
                    Risk Score
                  </span>

                  <strong>
                    {(resultRisk * 100).toFixed(
                      1
                    )}
                    %
                  </strong>

                  <div className="progress">
                    <div
                      style={{
                        width: `${Math.min(
                          resultRisk * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="metric">
                  <span>
                    Confidence
                  </span>

                  <strong>
                    {(resultConfidence * 100).toFixed(
                      1
                    )}
                    %
                  </strong>

                  <div className="progress">
                    <div
                      style={{
                        width: `${Math.min(
                          resultConfidence * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="metric">
                  <span>
                    Active Modalities
                  </span>

                  <strong>
                    {activeModalities.length}
                  </strong>

                  <small>
                    {activeModalities.length
                      ? activeModalities.join(
                          " • "
                        )
                      : "No modality"}
                  </small>
                </div>

              </div>

              {/* EXPLAINABLE AI */}
              <div className="result-section">

                <div className="section-title">
                  Explainable AI
                </div>

                <div className="explanation-card">

                  <div>
                    <strong>
                      {explanation?.summary ||
                        "AI berhasil menganalisis konten berdasarkan evidence yang tersedia."}
                    </strong>

                    <p>
                      Risk level:{" "}
                      {explanation?.risk_level ||
                        classificationText(
                          resultClassification
                        )}
                    </p>
                  </div>

                  <div className="reason-list">
                    {normalizeArray(
                      explanation?.reasons
                    ).map(
                      (reason, index) => (
                        <div
                          key={index}
                          className="reason-item"
                        >
                          <span>✓</span>
                          {reason}
                        </div>
                      )
                    )}
                  </div>

                </div>

              </div>

              {/* MODALITY EVIDENCE */}
              <div className="result-section">

                <div className="section-title">
                  Multimodal Evidence
                </div>

                <div className="evidence-grid">

                  {Object.entries(
                    evidence || {}
                  )
                    .filter(
                      ([key]) =>
                        key !==
                        "cross_modal"
                    )
                    .map(
                      ([key, value]) => (
                        <div
                          className="evidence-card"
                          key={key}
                        >
                          <div className="evidence-name">
                            {key.toUpperCase()}
                          </div>

                          <div className="evidence-score">
                            {Number(
                              value?.score ||
                                0
                            ).toFixed(3)}
                          </div>

                          <div className="evidence-meta">
                            Reliability:{" "}
                            {Number(
                              value?.reliability ||
                                0
                            ).toFixed(3)}
                          </div>

                          {normalizeArray(
                            value?.gambling_terms
                          ).map(
                            (term, index) => (
                              <span
                                className="evidence-tag"
                                key={index}
                              >
                                {term}
                              </span>
                            )
                          )}

                          {normalizeArray(
                            value?.evidence
                          ).map(
                            (term, index) => (
                              <span
                                className="evidence-tag"
                                key={index}
                              >
                                {term}
                              </span>
                            )
                          )}
                        </div>
                      )
                    )}

                </div>

              </div>

              {/* CYBER SECURITY */}
              <div className="result-section">

                <div className="section-title">
                  Cyber Security Layer
                </div>

                <div className="security-card">

                  <div>
                    <span>
                      Security Score
                    </span>

                    <strong>
                      {Number(
                        cyberSecurity?.security_score ||
                          resultRisk
                      ).toFixed(3)}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Severity
                    </span>

                    <strong>
                      {cyberSecurity?.severity ||
                        "LOW"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Recommended Action
                    </span>

                    <strong>
                      {cyberSecurity?.action ||
                        "ALLOW_WITH_MONITORING"}
                    </strong>
                  </div>

                </div>

                {normalizeArray(
                  cyberSecurity?.alerts
                ).length > 0 && (
                  <div className="alert-list">
                    {normalizeArray(
                      cyberSecurity?.alerts
                    ).map(
                      (alert, index) => (
                        <div
                          key={index}
                          className="security-alert"
                        >
                          ⚠ {alert}
                        </div>
                      )
                    )}
                  </div>
                )}

              </div>

              {/* CYBER INTELLIGENCE */}
              <div className="result-section">

                <div className="section-title">
                  Cyber Intelligence
                </div>

                <div className="intel-grid">

                  <div className="intel-card">
                    <span>
                      Accounts
                    </span>

                    <strong>
                      {normalizeArray(
                        digitalIntelligence?.account
                      ).length}
                    </strong>
                  </div>

                  <div className="intel-card">
                    <span>
                      URLs
                    </span>

                    <strong>
                      {normalizeArray(
                        digitalIntelligence?.url
                      ).length}
                    </strong>
                  </div>

                  <div className="intel-card">
                    <span>
                      Domains
                    </span>

                    <strong>
                      {normalizeArray(
                        digitalIntelligence?.domain
                      ).length}
                    </strong>
                  </div>

                  <div className="intel-card">
                    <span>
                      Contacts
                    </span>

                    <strong>
                      {normalizeArray(
                        digitalIntelligence?.contact
                      ).length}
                    </strong>
                  </div>

                </div>

              </div>

              {/* CORRELATION */}
              <div className="result-section">

                <div className="section-title">
                  Threat Correlation
                </div>

                <div className="correlation-card">

                  <div>
                    <span>
                      Related Cases
                    </span>

                    <strong>
                      {correlation?.related_case_count ||
                        0}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Shared Indicators
                    </span>

                    <strong>
                      {correlation?.shared_indicator_count ||
                        0}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Correlation Level
                    </span>

                    <strong>
                      {correlation?.correlation_level ||
                        "NONE"}
                    </strong>
                  </div>

                </div>

              </div>
            </>
          )}
        </section>
      )}

      {/* RECENT CASES */}
      <section className="recent-panel">

        <div className="panel-header">

          <div>
            <h2>
              Recent Cases
            </h2>

            <p>
              Latest detected content
            </p>
          </div>

          <button
            className="link-button"
            onClick={onOpenCases}
          >
            View all →
          </button>

        </div>

        {loading ? (
          <div className="empty-state">
            Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ◌
            </div>

            <strong>
              No cases yet
            </strong>

            <span>
              Analyze an image or text
              untuk membuat case pertama.
            </span>
          </div>
        ) : (
          <div className="case-list">

            {cases
              .slice()
              .reverse()
              .slice(0, 5)
              .map(
                (item, index) => {
                  const classification =
                    getClassification(
                      item
                    );

                  const risk =
                    getRiskScore(item);

                  return (
                    <div
                      className="case-row"
                      key={
                        item.case_id ||
                        item.id ||
                        index
                      }
                    >
                      <div className="case-main">
                        <div className="case-id">
                          {item.case_id ||
                            item.filename ||
                            `CASE-${index + 1}`}
                        </div>

                        <div className="case-date">
                          {item.created_at
                            ? new Date(
                                item.created_at
                              ).toLocaleString(
                                "id-ID"
                              )
                            : "Recently analyzed"}
                        </div>
                      </div>

                      <div className="case-risk">
                        {(risk * 100).toFixed(
                          1
                        )}
                        %
                      </div>

                      <div
                        className={`mini-class ${classification.toLowerCase()}`}
                      >
                        {classification}
                      </div>
                    </div>
                  );
                }
              )}

          </div>
        )}

      </section>

    </div>
  );
}

export default Dashboard;