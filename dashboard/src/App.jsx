import React, { useEffect, useState } from "react";

import Dashboard from "./Dashboard";
import CasesPage from "./CasesPage";
import ThreatGraph from "./ThreatGraph";
import HumanReview from "./HumanReview";
import AnalyzeContent from "./AnalyzeContent";

import "./App.css";


// ============================================================
// GUARDNET-AI
// MAIN APPLICATION
// ============================================================

const API_BASE = "http://127.0.0.1:8000";


// ============================================================
// PAGE ROUTES
// ============================================================

const ROUTES = {
  dashboard: "/",
  cases: "/cases",
  "threat-graph": "/threat-graph",
  "human-review": "/human-review",
  analyze: "/analyze",
};


// ============================================================
// GET PAGE FROM URL
// ============================================================

function getPageFromPath(pathname) {
  switch (pathname) {
    case "/cases":
      return "cases";

    case "/threat-graph":
      return "threat-graph";

    case "/human-review":
      return "human-review";

    case "/analyze":
      return "analyze";

    case "/":
    default:
      return "dashboard";
  }
}


// ============================================================
// MAIN APP
// ============================================================

function App() {

  const [page, setPage] = useState(
    getPageFromPath(window.location.pathname)
  );

  const [apiStatus, setApiStatus] = useState(
    "checking"
  );

  const [caseCount, setCaseCount] = useState(0);

  const [c2Count, setC2Count] = useState(0);


  // ==========================================================
  // CHECK BACKEND
  // ==========================================================

  const checkBackend = async () => {

    try {

      const response = await fetch(
        `${API_BASE}/`,
        {
          method: "GET",
        }
      );

      if (response.ok) {

        setApiStatus("online");

      } else {

        setApiStatus("offline");

      }

    } catch (error) {

      console.error(
        "Backend connection error:",
        error
      );

      setApiStatus("offline");

    }
  };


  // ==========================================================
  // LOAD CASE STATISTICS
  // ==========================================================

  const loadCaseStatistics = async () => {

    try {

      const response = await fetch(
        `${API_BASE}/api/statistics`
      );

      if (!response.ok) {

        return;

      }

      const data = await response.json();


      // ------------------------------------------------------
      // Try common statistics response formats
      // ------------------------------------------------------

      const total =
        data.total_cases ??
        data.total ??
        data.case_count ??
        data.statistics?.total_cases ??
        0;


      const c2 =
        data.c2_cases ??
        data.c2_count ??
        data.c2 ??
        data.statistics?.c2_cases ??
        0;


      setCaseCount(
        Number(total) || 0
      );

      setC2Count(
        Number(c2) || 0
      );

    } catch (error) {

      console.warn(
        "Statistics unavailable:",
        error
      );

    }
  };


  // ==========================================================
  // INITIALIZATION
  // ==========================================================

  useEffect(() => {

    checkBackend();

    loadCaseStatistics();

  }, []);


  // ==========================================================
  // BROWSER BACK / FORWARD
  // ==========================================================

  useEffect(() => {

    const handlePopState = () => {

      setPage(
        getPageFromPath(
          window.location.pathname
        )
      );

    };


    window.addEventListener(
      "popstate",
      handlePopState
    );


    return () => {

      window.removeEventListener(
        "popstate",
        handlePopState
      );

    };

  }, []);


  // ==========================================================
  // NAVIGATION
  // ==========================================================

  const navigate = (targetPage) => {

    const targetPath =
      ROUTES[targetPage] || "/";


    window.history.pushState(
      {},
      "",
      targetPath
    );


    setPage(targetPage);


    // Refresh data after navigation
    loadCaseStatistics();

  };


  // ==========================================================
  // REFRESH ALL DATA
  // ==========================================================

  const refreshApplication = async () => {

    await checkBackend();

    await loadCaseStatistics();

  };


  // ==========================================================
  // RENDER CURRENT PAGE
  // ==========================================================

  const renderPage = () => {

    switch (page) {

      // ------------------------------------------------------
      // DASHBOARD
      // ------------------------------------------------------

      case "dashboard":

        return (
          <Dashboard
            apiBase={API_BASE}
            onOpenCases={() =>
              navigate("cases")
            }
            onOpenAnalyze={() =>
              navigate("analyze")
            }
          />
        );


      // ------------------------------------------------------
      // CASES
      // ------------------------------------------------------

      case "cases":

        return (
          <CasesPage
            apiBase={API_BASE}
            onBack={() =>
              navigate("dashboard")
            }
          />
        );


      // ------------------------------------------------------
      // THREAT GRAPH
      // ------------------------------------------------------

      case "threat-graph":

        return (
          <ThreatGraph
            apiBase={API_BASE}
            onBack={() =>
              navigate("dashboard")
            }
          />
        );


      // ------------------------------------------------------
      // HUMAN REVIEW
      // ------------------------------------------------------

      case "human-review":

        return (
          <HumanReview
            apiBase={API_BASE}
            onBack={() =>
              navigate("dashboard")
            }
          />
        );


      // ------------------------------------------------------
      // ANALYZE CONTENT
      // ------------------------------------------------------

      case "analyze":

        return (
          <AnalyzeContent
            apiBase={API_BASE}
            onBack={() =>
              navigate("dashboard")
            }
          />
        );


      // ------------------------------------------------------
      // DEFAULT
      // ------------------------------------------------------

      case "dashboard":

      default:

        return (
          <Dashboard
            apiBase={API_BASE}
            onOpenCases={() =>
              navigate("cases")
            }
            onOpenAnalyze={() =>
              navigate("analyze")
            }
          />
        );
    }

  };


  // ==========================================================
  // APP UI
  // ==========================================================

  return (

    <div className="app-shell">


      {/* ====================================================
          SIDEBAR
          ==================================================== */}

      <aside className="sidebar">


        {/* --------------------------------------------------
            BRAND
            -------------------------------------------------- */}

        <div className="brand">

          <div className="brand-logo">
            🛡️
          </div>

          <div>

            <div className="brand-title">
              GuardNet-AI
            </div>

            <div className="brand-subtitle">
              Research Publication Edition
            </div>

          </div>

        </div>


        {/* ==================================================
            MONITORING
            ================================================== */}

        <div className="sidebar-section-title">
          MONITORING
        </div>


        {/* DASHBOARD */}

        <button
          type="button"
          className={
            `sidebar-item ${
              page === "dashboard"
                ? "active"
                : ""
            }`
          }
          onClick={() =>
            navigate("dashboard")
          }
        >

          <span>
            ▦
          </span>

          <span>
            Dashboard
          </span>

        </button>


        {/* CASES */}

        <button
          type="button"
          className={
            `sidebar-item ${
              page === "cases"
                ? "active"
                : ""
            }`
          }
          onClick={() =>
            navigate("cases")
          }
        >

          <span>
            ▣
          </span>

          <span>
            Cases
          </span>

          {caseCount > 0 && (

            <span className="sidebar-badge">
              {caseCount}
            </span>

          )}

        </button>


        {/* THREAT GRAPH */}

        <button
          type="button"
          className={
            `sidebar-item ${
              page === "threat-graph"
                ? "active"
                : ""
            }`
          }
          onClick={() =>
            navigate("threat-graph")
          }
        >

          <span>
            ◎
          </span>

          <span>
            Threat Graph
          </span>

        </button>


        {/* HUMAN REVIEW */}

        <button
          type="button"
          className={
            `sidebar-item ${
              page === "human-review"
                ? "active"
                : ""
            }`
          }
          onClick={() =>
            navigate("human-review")
          }
        >

          <span>
            ✓
          </span>

          <span>
            Human Review
          </span>

          {c2Count > 0 && (

            <span className="sidebar-badge red">
              {c2Count}
            </span>

          )}

        </button>


        {/* ==================================================
            ANALYSIS
            ================================================== */}

        <div className="sidebar-section-title">
          ANALYSIS
        </div>


        {/* ANALYZE CONTENT */}

        <button
          type="button"
          className={
            `sidebar-item ${
              page === "analyze"
                ? "active"
                : ""
            }`
          }
          onClick={() =>
            navigate("analyze")
          }
        >

          <span>
            ◇
          </span>

          <span>
            Analyze Content
          </span>

        </button>


        {/* ==================================================
            SIDEBAR BOTTOM
            ================================================== */}

        <div className="sidebar-bottom">

          <div className="system-card">


            <div className="system-card-title">
              System Status
            </div>


            {/* BACKEND STATUS */}

            <div className="system-status">

              <span
                className={
                  `status-dot ${
                    apiStatus === "online"
                      ? "green"
                      : apiStatus === "offline"
                      ? "red"
                      : "yellow"
                  }`
                }
              />

              <span>

                {apiStatus === "online"
                  ? "Backend Online"
                  : apiStatus === "offline"
                  ? "Backend Offline"
                  : "Checking..."
                }

              </span>

            </div>


            {/* REFRESH CONNECTION */}

            <button
              type="button"
              className="small-refresh"
              onClick={
                refreshApplication
              }
            >
              Refresh connection
            </button>


          </div>

        </div>


      </aside>


      {/* ====================================================
          MAIN CONTENT
          ==================================================== */}

      <main className="main-content">

        {renderPage()}

      </main>


    </div>

  );

}


export default App;