import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("dashboard");

  const [statistics, setStatistics] = useState(null);
  const [cases, setCases] = useState([]);
  const [graph, setGraph] = useState({
    nodes: [],
    links: [],
  });

  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(true);

  // =====================================================
  // LOAD DASHBOARD DATA
  // =====================================================

  async function loadData() {
    try {
      setLoading(true);

      const [
        statisticsResponse,
        casesResponse,
        graphResponse,
      ] = await Promise.all([
        fetch(`${API}/api/statistics`),
        fetch(`${API}/api/cases`),
        fetch(`${API}/api/threat-graph`),
      ]);

      if (!statisticsResponse.ok) {
        throw new Error("Statistics API error");
      }

      if (!casesResponse.ok) {
        throw new Error("Cases API error");
      }

      if (!graphResponse.ok) {
        throw new Error("Graph API error");
      }

      const statisticsData =
        await statisticsResponse.json();

      const casesData =
        await casesResponse.json();

      const graphData =
        await graphResponse.json();

      setStatistics(statisticsData);
      setCases(casesData.cases || []);
      setGraph(
        graphData || {
          nodes: [],
          links: [],
        }
      );
    } catch (error) {
      console.error(
        "Dashboard error:",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // AUTO REFRESH
  // =====================================================

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // =====================================================
  // OPEN CASE
  // =====================================================

  async function openCase(caseId) {
    try {
      const response = await fetch(
        `${API}/api/cases/${caseId}`
      );

      if (!response.ok) {
        throw new Error(
          "Case not found"
        );
      }

      const data =
        await response.json();

      setSelectedCase(data);
      setPage("case-detail");
    } catch (error) {
      console.error(error);

      alert(
        "Gagal mengambil detail case."
      );
    }
  }

  // =====================================================
  // HUMAN REVIEW
  // =====================================================

  async function reviewCase(decision) {
    if (!selectedCase) {
      return;
    }

    const formData =
      new FormData();

    formData.append(
      "decision",
      decision
    );

    formData.append(
      "reviewer",
      "GuardNet-AI Reviewer"
    );

    formData.append(
      "notes",
      decision === "APPROVE"
        ? "Case approved for escalation after human verification."
        : "Case rejected after human verification."
    );

    try {
      const response =
        await fetch(
          `${API}/api/review/${selectedCase.case_id}`,
          {
            method: "POST",
            body: formData,
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Review failed"
        );
      }

      setSelectedCase(
        data.case
      );

      await loadData();

      alert(
        decision === "APPROVE"
          ? "Case berhasil di-approve."
          : "Case berhasil di-reject."
      );
    } catch (error) {
      console.error(error);

      alert(error.message);
    }
  }

  // =====================================================
  // LOADING
  // =====================================================

  if (
    loading &&
    !statistics
  ) {
    return (
      <div className="loading-screen">

        <div className="loading-shield">
          🛡️
        </div>

        <h1>
          GuardNet-AI
        </h1>

        <p>
          Connecting to AI detection backend...
        </p>

        <div className="loading-bar">
          <div></div>
        </div>

      </div>
    );
  }

  // =====================================================
  // MAIN APPLICATION
  // =====================================================

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-logo">
            🛡️
          </div>

          <div className="brand-text">

            <h2>
              GuardNet-AI
            </h2>

            <span>
              Research Publication Edition
            </span>

          </div>

        </div>


        <div className="sidebar-section-title">
          MONITORING
        </div>


        <nav className="sidebar-nav">

          <button
            className={
              page === "dashboard"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setPage("dashboard")
            }
          >
            <span className="nav-icon">
              ▦
            </span>

            <span>
              Dashboard
            </span>
          </button>


          <button
            className={
              page === "cases"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setPage("cases")
            }
          >
            <span className="nav-icon">
              ▣
            </span>

            <span>
              Cases
            </span>

            {cases.length > 0 && (
              <span className="nav-count">
                {cases.length}
              </span>
            )}
          </button>


          <button
            className={
              page === "graph"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setPage("graph")
            }
          >
            <span className="nav-icon">
              ◎
            </span>

            <span>
              Threat Graph
            </span>
          </button>


          <button
            className={
              page === "review"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setPage("review")
            }
          >
            <span className="nav-icon">
              ✓
            </span>

            <span>
              Human Review
            </span>

            {cases.filter(
              (item) =>
                item.status ===
                "PENDING_REVIEW"
            ).length > 0 && (
              <span className="nav-count review">
                {
                  cases.filter(
                    (item) =>
                      item.status ===
                      "PENDING_REVIEW"
                  ).length
                }
              </span>
            )}

          </button>

        </nav>


        <div className="sidebar-section-title">
          ANALYSIS
        </div>


        <nav className="sidebar-nav">

          <button
            className={
              page === "analysis"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setPage("analysis")
            }
          >
            <span className="nav-icon">
              ◈
            </span>

            <span>
              Analyze Content
            </span>

          </button>

        </nav>


        <div className="sidebar-bottom">

          <div className="connection-card">

            <div className="connection-status">

              <span className="online-dot"></span>

              <div>

                <strong>
                  System Online
                </strong>

                <small>
                  FastAPI Connected
                </small>

              </div>

            </div>


            <div className="api-address">
              127.0.0.1:8000
            </div>

          </div>


          <div className="version">
            GuardNet-AI v1.3.0
          </div>

        </div>

      </aside>


      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* TOPBAR */}

        <header className="topbar">

          <div>

            <div className="breadcrumb">

              GUARDNET-AI

              <span>/</span>

              {
                page === "dashboard"
                  ? "Dashboard"
                  : page === "cases"
                  ? "Cases"
                  : page === "graph"
                  ? "Threat Graph"
                  : page === "review"
                  ? "Human Review"
                  : page === "analysis"
                  ? "Analyze Content"
                  : "Case Investigation"
              }

            </div>


            <h1>

              {
                page === "dashboard"
                  ? "Security Dashboard"
                  : page === "cases"
                  ? "Case Management"
                  : page === "graph"
                  ? "Threat Entity Graph"
                  : page === "review"
                  ? "Human Review Queue"
                  : page === "analysis"
                  ? "Multimodal Analysis"
                  : "Case Investigation"
              }

            </h1>

          </div>


          <div className="topbar-actions">

            <div className="live-status">

              <span></span>

              LIVE

            </div>


            <button
              className="refresh-button"
              onClick={loadData}
            >
              ↻ Refresh
            </button>

          </div>

        </header>


        {/* DASHBOARD */}

        {page === "dashboard" && (
          <DashboardPage
            statistics={statistics}
            cases={cases}
            openCase={openCase}
          />
        )}


        {/* CASES */}

        {page === "cases" && (
          <CasesPage
            cases={cases}
            openCase={openCase}
          />
        )}


        {/* GRAPH */}

        {page === "graph" && (
          <ThreatGraphPage
            graph={graph}
          />
        )}


        {/* REVIEW */}

        {page === "review" && (
          <ReviewPage
            cases={cases}
            openCase={openCase}
          />
        )}


        {/* ANALYSIS */}

        {page === "analysis" && (
          <AnalysisPage
            onCaseCreated={
              loadData
            }
          />
        )}


        {/* CASE DETAIL */}

        {page === "case-detail" &&
          selectedCase && (
            <CaseDetailPage
              caseData={
                selectedCase
              }
              onBack={() =>
                setPage("cases")
              }
              onReview={
                reviewCase
              }
            />
          )}

      </main>

    </div>
  );
}


// =====================================================
// DASHBOARD PAGE
// =====================================================

function DashboardPage({
  statistics,
  cases,
  openCase,
}) {
  const totalCases =
    statistics?.total_cases || 0;

  const c0 =
    statistics?.classification?.C0 || 0;

  const c1 =
    statistics?.classification?.C1 || 0;

  const c2 =
    statistics?.classification?.C2 || 0;

  const high =
    statistics?.priority?.HIGH || 0;

  const medium =
    statistics?.priority?.MEDIUM || 0;

  const pending =
    cases.filter(
      (item) =>
        item.status ===
        "PENDING_REVIEW"
    ).length;

  return (
    <>

      <section className="stats-grid">

        <StatCard
          title="Total Cases"
          value={totalCases}
          description="All detected cases"
          icon="▣"
          type="blue"
        />

        <StatCard
          title="C2 Promotions"
          value={c2}
          description="High-risk gambling promotion"
          icon="⚠"
          type="red"
        />

        <StatCard
          title="High Priority"
          value={high}
          description="Requires immediate review"
          icon="!"
          type="orange"
        />

        <StatCard
          title="Pending Review"
          value={pending}
          description="Awaiting human verification"
          icon="◷"
          type="purple"
        />

      </section>


      <section className="secondary-stats">

        <div className="mini-stat">
          <span>
            C0 — Normal
          </span>

          <strong>
            {c0}
          </strong>
        </div>


        <div className="mini-stat">
          <span>
            C1 — Related
          </span>

          <strong>
            {c1}
          </strong>
        </div>


        <div className="mini-stat">
          <span>
            C2 — Promotion
          </span>

          <strong>
            {c2}
          </strong>
        </div>


        <div className="mini-stat">
          <span>
            Medium Priority
          </span>

          <strong>
            {medium}
          </strong>
        </div>

      </section>


      <section className="dashboard-grid">

        <div className="panel">

          <PanelHeader
            title="Recent Cases"
            description="Latest detected content"
          />

          <CaseTable
            cases={cases}
            openCase={openCase}
          />

        </div>


        <div className="panel">

          <PanelHeader
            title="Classification"
            description="Current case distribution"
          />

          <div className="classification-list">

            <Distribution
              label="C0 — Non-Gambling"
              value={c0}
              total={totalCases}
              type="green"
            />

            <Distribution
              label="C1 — Gambling Related"
              value={c1}
              total={totalCases}
              type="orange"
            />

            <Distribution
              label="C2 — Gambling Promotion"
              value={c2}
              total={totalCases}
              type="red"
            />

          </div>

        </div>

      </section>


      <div className="panel pipeline-panel">

        <PanelHeader
          title="Detection Pipeline"
          description="Current GuardNet-AI processing architecture"
        />

        <div className="pipeline">

          <PipelineItem
            icon="◉"
            title="Instagram"
            description="Content"
          />

          <PipelineArrow />

          <PipelineItem
            icon="▤"
            title="OCR"
            description="Text extraction"
          />

          <PipelineArrow />

          <PipelineItem
            icon="◈"
            title="Vision"
            description="Visual analysis"
          />

          <PipelineArrow />

          <PipelineItem
            icon="AI"
            title="Fusion"
            description="Multimodal AI"
          />

          <PipelineArrow />

          <PipelineItem
            icon="⚠"
            title="C0/C1/C2"
            description="Classification"
          />

          <PipelineArrow />

          <PipelineItem
            icon="✓"
            title="Review"
            description="Human verification"
          />

        </div>

      </div>

    </>
  );
}


// =====================================================
// STAT CARD
// =====================================================

function StatCard({
  title,
  value,
  description,
  icon,
  type,
}) {
  return (
    <div
      className={`stat-card ${type}`}
    >

      <div className="stat-card-top">

        <div className="stat-icon">
          {icon}
        </div>

        <span className="stat-label">
          {title}
        </span>

      </div>


      <strong className="stat-value">
        {value}
      </strong>


      <span className="stat-description">
        {description}
      </span>

    </div>
  );
}


// =====================================================
// PANEL HEADER
// =====================================================

function PanelHeader({
  title,
  description,
}) {
  return (
    <div className="panel-header">

      <div>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

      </div>

    </div>
  );
}


// =====================================================
// CASE TABLE
// =====================================================

function CaseTable({
  cases,
  openCase,
}) {
  if (!cases.length) {
    return (
      <div className="empty-state">

        <div>
          ✓
        </div>

        <strong>
          No cases detected
        </strong>

        <p>
          GuardNet-AI has not created
          any investigation cases yet.
        </p>

      </div>
    );
  }

  return (
    <div className="table-wrapper">

      <table>

        <thead>

          <tr>

            <th>
              CASE
            </th>

            <th>
              CLASSIFICATION
            </th>

            <th>
              RPS
            </th>

            <th>
              PRIORITY
            </th>

            <th>
              STATUS
            </th>

            <th></th>

          </tr>

        </thead>


        <tbody>

          {cases.map(
            (item) => {

              const classification =
                item.classification
                  ?.classification ||
                "-";

              const priority =
                item.review_priority
                  ?.priority ||
                "-";

              const rps =
                item.review_priority
                  ?.score ?? 0;

              return (
                <tr
                  key={
                    item.case_id
                  }
                >

                  <td>

                    <div className="case-cell">

                      <strong>
                        {
                          item.case_id
                        }
                      </strong>

                      <small>
                        {
                          item.filename
                        }
                      </small>

                    </div>

                  </td>


                  <td>

                    <span
                      className={
                        classification ===
                        "C2"
                          ? "classification-badge c2"
                          : classification ===
                            "C1"
                          ? "classification-badge c1"
                          : "classification-badge c0"
                      }
                    >
                      {
                        classification
                      }
                    </span>

                  </td>


                  <td>

                    <strong>
                      {
                        Number(
                          rps
                        ).toFixed(3)
                      }
                    </strong>

                  </td>


                  <td>

                    <span
                      className={
                        `priority-badge ${
                          priority.toLowerCase()
                        }`
                      }
                    >
                      {
                        priority
                      }
                    </span>

                  </td>


                  <td>

                    <span className="status-badge">
                      {
                        item.status
                      }
                    </span>

                  </td>


                  <td>

                    <button
                      className="view-button"
                      onClick={() =>
                        openCase(
                          item.case_id
                        )
                      }
                    >
                      View →
                    </button>

                  </td>

                </tr>
              );
            }
          )}

        </tbody>

      </table>

    </div>
  );
}


// =====================================================
// DISTRIBUTION
// =====================================================

function Distribution({
  label,
  value,
  total,
  type,
}) {
  const percentage =
    total > 0
      ? Math.round(
          (value / total) *
            100
        )
      : 0;

  return (
    <div className="distribution">

      <div className="distribution-top">

        <div className="distribution-name">

          <span
            className={
              `distribution-dot ${type}`
            }
          ></span>

          {label}

        </div>


        <strong>
          {value}
        </strong>

      </div>


      <div className="progress-track">

        <div
          className={
            `progress-fill ${type}`
          }
          style={{
            width:
              `${percentage}%`,
          }}
        ></div>

      </div>


      <small>
        {percentage}% of cases
      </small>

    </div>
  );
}


// =====================================================
// PIPELINE
// =====================================================

function PipelineItem({
  icon,
  title,
  description,
}) {
  return (
    <div className="pipeline-item">

      <div className="pipeline-icon">
        {icon}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {description}
      </span>

    </div>
  );
}


function PipelineArrow() {
  return (
    <div className="pipeline-arrow">
      →
    </div>
  );
}


// =====================================================
// CASES PAGE
// =====================================================

function CasesPage({
  cases,
  openCase,
}) {
  return (
    <div className="panel full-panel">

      <PanelHeader
        title="Case Management"
        description={`${cases.length} investigation case(s) stored in GuardNet-AI`}
      />

      <CaseTable
        cases={cases}
        openCase={openCase}
      />

    </div>
  );
}


// =====================================================
// REVIEW PAGE
// =====================================================

function ReviewPage({
  cases,
  openCase,
}) {
  const pendingCases =
    cases.filter(
      (item) =>
        item.status ===
        "PENDING_REVIEW"
    );

  return (
    <div className="panel full-panel">

      <PanelHeader
        title="Human Review Queue"
        description="Cases requiring human verification before escalation"
      />

      {pendingCases.length ===
      0 ? (

        <div className="empty-state">

          <div>
            ✓
          </div>

          <strong>
            Review queue is clear
          </strong>

          <p>
            There are currently no
            pending cases.
          </p>

        </div>

      ) : (

        <CaseTable
          cases={pendingCases}
          openCase={openCase}
        />

      )}

    </div>
  );
}


// =====================================================
// THREAT GRAPH
// =====================================================

function ThreatGraphPage({
  graph,
}) {
  const nodes =
    graph?.nodes || [];

  const links =
    graph?.links || [];

  return (
    <>

      <div className="stats-grid graph-stats-grid">

        <StatCard
          title="Graph Nodes"
          value={
            nodes.length
          }
          description="Detected entities"
          icon="●"
          type="blue"
        />

        <StatCard
          title="Relationships"
          value={
            links.length
          }
          description="Entity relationships"
          icon="↔"
          type="purple"
        />

      </div>


      <div className="graph-layout">

        <div className="panel">

          <PanelHeader
            title="Entity Nodes"
            description="Entities extracted from detected content"
          />

          {nodes.length ===
          0 ? (

            <div className="empty-state">

              <div>
                ◎
              </div>

              <strong>
                No graph data yet
              </strong>

              <p>
                Threat graph nodes will appear
                when entity data is available.
              </p>

            </div>

          ) : (

            <div className="node-grid">

              {nodes.map(
                (
                  node,
                  index
                ) => (

                  <div
                    className="node-card"
                    key={`${node.id}-${index}`}
                  >

                    <span
                      className={
                        `node-type ${
                          node.type ||
                          "unknown"
                        }`
                      }
                    >
                      {
                        node.type ||
                        "entity"
                      }
                    </span>

                    <strong>
                      {
                        node.id ||
                        node.value ||
                        "Unknown"
                      }
                    </strong>

                  </div>

                )
              )}

            </div>

          )}

        </div>


        <div className="panel">

          <PanelHeader
            title="Relationships"
            description="Connections between entities"
          />

          {links.length ===
          0 ? (

            <div className="empty-state">

              <div>
                ↔
              </div>

              <strong>
                No relationships yet
              </strong>

            </div>

          ) : (

            <div className="relationship-list">

              {links.map(
                (
                  link,
                  index
                ) => (

                  <div
                    className="relationship"
                    key={index}
                  >

                    <span>
                      {
                        link.source
                      }
                    </span>

                    <b>
                      {
                        link.relation
                      }
                    </b>

                    <span>
                      {
                        link.target
                      }
                    </span>

                  </div>

                )
              )}

            </div>

          )}

        </div>

      </div>

    </>
  );
}


// =====================================================
// ANALYSIS PAGE
// =====================================================

function AnalysisPage({
  onCaseCreated,
}) {
  const [image, setImage] =
    useState(null);

  const [preview, setPreview] =
    useState(null);

  const [caption, setCaption] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);


  function handleImageChange(
    event
  ) {
    const selected =
      event.target.files?.[0];

    if (!selected) {
      return;
    }

    setImage(selected);

    setPreview(
      URL.createObjectURL(
        selected
      )
    );

    setResult(null);
  }


  async function analyzeImage() {

    if (!image) {

      alert(
        "Upload screenshot Instagram terlebih dahulu."
      );

      return;
    }


    setLoading(true);

    setResult(null);


    const formData =
      new FormData();

    formData.append(
      "image",
      image
    );

    formData.append(
      "caption",
      caption
    );


    try {

      /*
       * PENTING:
       * Request diarahkan ke:
       *
       * http://127.0.0.1:8000/api/detect-post
       *
       * Ini sudah sesuai dengan
       * endpoint FastAPI kamu.
       */

      const response =
        await fetch(
          `${API}/api/detect-post`,
          {
            method: "POST",
            body: formData,
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Analysis failed."
        );
      }


      setResult(data);

      onCaseCreated();

    } catch (error) {

      console.error(error);

      alert(
        `Backend tidak terhubung atau analysis gagal.\n\n${error.message}`
      );

    } finally {

      setLoading(false);

    }
  }


  const classification =
    result?.classification
      ?.classification ||
    "-";

  const risk =
    result?.classification
      ?.risk_score || 0;


  return (
    <div className="analysis-page">

      <div className="analysis-grid">

        {/* UPLOAD */}

        <div className="panel">

          <PanelHeader
            title="Instagram Content Analysis"
            description="Upload an Instagram screenshot for multimodal AI analysis"
          />


          <label className="upload-zone">

            {preview ? (

              <img
                src={preview}
                alt="Instagram preview"
                className="image-preview"
              />

            ) : (

              <>

                <div className="upload-icon">
                  ↑
                </div>

                <strong>
                  Upload Instagram Screenshot
                </strong>

                <span>
                  PNG, JPG or JPEG
                </span>

              </>

            )}


            <input
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              onChange={
                handleImageChange
              }
            />

          </label>


          <label className="field-label">
            Instagram Caption
          </label>


          <textarea
            className="caption-input"
            placeholder="Masukkan caption Instagram..."
            value={caption}
            onChange={(event) =>
              setCaption(
                event.target.value
              )
            }
          />


          <button
            className="analyze-button"
            onClick={
              analyzeImage
            }
            disabled={
              loading
            }
          >

            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                ◈ Analyze Content
              </>
            )}

          </button>

        </div>


        {/* RESULT */}

        <div className="panel">

          <PanelHeader
            title="Analysis Result"
            description="Multimodal AI detection output"
          />


          {!result ? (

            <div className="result-placeholder">

              <div className="placeholder-icon">
                ◈
              </div>

              <strong>
                Waiting for analysis
              </strong>

              <p>
                Upload an Instagram screenshot
                and start the analysis.
              </p>

            </div>

          ) : (

            <div className="analysis-result">

              <div
                className={
                  `risk-banner ${
                    classification ===
                    "C2"
                      ? "danger"
                      : classification ===
                        "C1"
                      ? "warning"
                      : "safe"
                  }`
                }
              >

                <div>

                  <span>
                    DETECTION CLASS
                  </span>

                  <strong>
                    {
                      classification
                    }
                  </strong>

                </div>


                <div className="risk-value">

                  <span>
                    RISK SCORE
                  </span>

                  <strong>
                    {
                      (
                        risk * 100
                      ).toFixed(
                        0
                      )
                    }%
                  </strong>

                </div>

              </div>


              {result.case && (

                <div className="created-case">

                  <span>
                    CASE CREATED
                  </span>

                  <strong>
                    {
                      result.case.case_id
                    }
                  </strong>

                  <small>
                    {
                      result.case.status
                    }
                  </small>

                </div>

              )}


              <ResultSection
                title="OCR Evidence"
              >

                <div className="ocr-box">

                  {
                    result.ocr
                      ?.text ||
                    "No OCR text detected."
                  }

                </div>

              </ResultSection>


              <ResultSection
                title="Threat Indicators"
              >

                <div className="chips">

                  {(
                    result.entities
                      ?.threat_indicator ||
                    []
                  ).length ===
                  0 ? (

                    <span className="muted">
                      No threat indicators.
                    </span>

                  ) : (

                    (
                      result.entities
                        ?.threat_indicator ||
                      []
                    ).map(
                      (item) => (

                        <span
                          className="threat-chip"
                          key={item}
                        >
                          {item}
                        </span>

                      )
                    )

                  )}

                </div>

              </ResultSection>


              <ResultSection
                title="Payment Intelligence"
              >

                <div className="info-grid">

                  <InfoItem
                    label="Payment Detected"
                    value={
                      result.payment
                        ?.detected
                        ? "YES"
                        : "NO"
                    }
                  />

                  <InfoItem
                    label="QRIS Decoder"
                    value={
                      result.qris
                        ?.detected
                        ? "DETECTED"
                        : "NOT DETECTED"
                    }
                  />

                  <InfoItem
                    label="Payment Risk"
                    value={
                      result.payment
                        ?.risk ??
                      0
                    }
                  />

                </div>

              </ResultSection>


              <ResultSection
                title="Fusion Evidence"
              >

                <div className="evidence-grid">

                  <EvidenceBar
                    label="Text"
                    value={
                      result.classification
                        ?.evidence
                        ?.text
                    }
                  />

                  <EvidenceBar
                    label="OCR"
                    value={
                      result.classification
                        ?.evidence
                        ?.ocr
                    }
                  />

                  <EvidenceBar
                    label="Visual"
                    value={
                      result.classification
                        ?.evidence
                        ?.visual
                    }
                  />

                  <EvidenceBar
                    label="Payment"
                    value={
                      result.classification
                        ?.evidence
                        ?.payment
                    }
                  />

                  <EvidenceBar
                    label="Entity"
                    value={
                      result.classification
                        ?.evidence
                        ?.entity
                    }
                  />

                </div>

              </ResultSection>

            </div>

          )}

        </div>

      </div>

    </div>
  );
}


// =====================================================
// RESULT SECTION
// =====================================================

function ResultSection({
  title,
  children,
}) {
  return (
    <div className="result-section">

      <h3>
        {title}
      </h3>

      {children}

    </div>
  );
}


// =====================================================
// INFO ITEM
// =====================================================

function InfoItem({
  label,
  value,
}) {
  return (
    <div className="info-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


// =====================================================
// EVIDENCE BAR
// =====================================================

function EvidenceBar({
  label,
  value,
}) {
  const percentage =
    Math.round(
      (Number(value) || 0) *
        100
    );

  return (
    <div className="evidence-bar">

      <div>

        <span>
          {label}
        </span>

        <strong>
          {percentage}%
        </strong>

      </div>


      <div className="progress-track">

        <div
          className="progress-fill blue"
          style={{
            width:
              `${percentage}%`,
          }}
        ></div>

      </div>

    </div>
  );
}


// =====================================================
// CASE DETAIL
// =====================================================

function CaseDetailPage({
  caseData,
  onBack,
  onReview,
}) {
  const classification =
    caseData.classification ||
    {};

  const evidence =
    classification.evidence ||
    {};

  const priority =
    caseData.review_priority ||
    {};

  const entities =
    caseData.entities ||
    {};


  return (
    <div className="case-detail-page">

      <button
        className="back-button"
        onClick={onBack}
      >
        ← Back to Cases
      </button>


      <div className="case-header">

        <div>

          <span className="case-number">
            {
              caseData.case_id
            }
          </span>

          <h2>
            {
              caseData.caption ||
              caseData.filename
            }
          </h2>

          <p>
            Created at{" "}
            {
              caseData.created_at
            }
          </p>

        </div>


        <div
          className={
            classification.classification ===
            "C2"
              ? "large-classification c2"
              : "large-classification"
          }
        >
          {
            classification.classification
          }
        </div>

      </div>


      <div className="detail-grid">

        <div className="panel">

          <PanelHeader
            title="Risk Assessment"
            description="Multimodal evidence analysis"
          />


          <div className="large-risk">

            <strong>
              {
                (
                  Number(
                    classification.risk_score
                  ) * 100
                ).toFixed(0)
              }%
            </strong>

            <span>
              Classification Risk Score
            </span>

          </div>


          <div className="evidence-list">

            <EvidenceBar
              label="Native Text"
              value={
                evidence.text
              }
            />

            <EvidenceBar
              label="OCR"
              value={
                evidence.ocr
              }
            />

            <EvidenceBar
              label="Visual"
              value={
                evidence.visual
              }
            />

            <EvidenceBar
              label="Payment"
              value={
                evidence.payment
              }
            />

            <EvidenceBar
              label="Entity"
              value={
                evidence.entity
              }
            />

          </div>

        </div>


        <div className="panel">

          <PanelHeader
            title="Review Priority"
            description="Review Priority Score"
          />


          <div
            className={
              `priority-box ${
                priority.priority?.toLowerCase()
              }`
            }
          >

            <strong>
              {
                priority.priority
              }
            </strong>

            <span>
              RPS{" "}
              {
                Number(
                  priority.score ||
                  0
                ).toFixed(3)
              }
            </span>

          </div>


          <div className="component-list">

            {Object.entries(
              priority.components ||
              {}
            ).map(
              (
                [key, value]
              ) => (

                <div key={key}>

                  <span>
                    {
                      key.replaceAll(
                        "_",
                        " "
                      )
                    }
                  </span>

                  <strong>
                    {value}
                  </strong>

                </div>

              )
            )}

          </div>

        </div>

      </div>


      <div className="detail-grid">

        <div className="panel">

          <PanelHeader
            title="Threat Indicators"
            description="Extracted threat-related entities"
          />

          <div className="chips">

            {(
              entities.threat_indicator ||
              []
            ).map(
              (item) => (

                <span
                  className="threat-chip"
                  key={item}
                >
                  {item}
                </span>

              )
            )}

          </div>

        </div>


        <div className="panel">

          <PanelHeader
            title="Payment Intelligence"
            description="Payment-related evidence"
          />

          <div className="info-grid">

            <InfoItem
              label="Payment Detection"
              value={
                caseData.payment
                  ?.detected
                  ? "DETECTED"
                  : "NOT DETECTED"
              }
            />

            <InfoItem
              label="QRIS Decoder"
              value={
                caseData.qris
                  ?.detected
                  ? "DETECTED"
                  : "NOT DETECTED"
              }
            />

            <InfoItem
              label="Evidence"
              value={
                caseData.payment
                  ?.evidence
                  ?.join(", ") ||
                "-"
              }
            />

          </div>

        </div>

      </div>


      <div className="panel">

        <PanelHeader
          title="OCR Evidence"
          description="Text extracted from the image"
        />

        <div className="ocr-box detail-ocr">

          {
            caseData.ocr
              ?.text ||
            "No OCR text available."
          }

        </div>

      </div>


      <div className="panel review-panel">

        <PanelHeader
          title="Human Verification"
          description="Final decision must be performed by a human reviewer"
        />


        {caseData.status ===
        "PENDING_REVIEW" ? (

          <div className="review-actions">

            <button
              className="reject-button"
              onClick={() =>
                onReview(
                  "REJECT"
                )
              }
            >
              ✕ Reject Case
            </button>


            <button
              className="approve-button"
              onClick={() =>
                onReview(
                  "APPROVE"
                )
              }
            >
              ✓ Approve for Escalation
            </button>

          </div>

        ) : (

          <div className="review-complete">

            <strong>
              {
                caseData.status
              }
            </strong>

            <span>
              This case has already
              been reviewed.
            </span>

          </div>

        )}

      </div>

    </div>
  );
}


export default App;