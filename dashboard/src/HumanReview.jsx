import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function HumanReview() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] =
    useState(null);
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");

  const loadCases = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        `${API_BASE}/api/cases`
      );

      const data = await response.json();

      const pendingCases =
        (data.cases || []).filter(
          (item) =>
            item.status ===
              "PENDING_REVIEW" ||
            item.cyber_security
              ?.controls?.manual_review ===
              true
        );

      setCases(pendingCases);
    } catch (error) {
      console.error(error);
      setMessage(
        "Gagal mengambil data human review."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  const reviewCase = async (decision) => {
    if (!selectedCase) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/review/${selectedCase.case_id}`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            decision,
            notes,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Review gagal."
        );
      }

      setMessage(
        `Case berhasil di-${decision}.`
      );

      setSelectedCase(null);
      setNotes("");

      loadCases();
    } catch (error) {
      console.error(error);

      setMessage(
        error.message ||
          "Gagal melakukan review."
      );
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "36px",
      }}
    >
      <div
        style={{
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            fontSize: "13px",
            color: "#718096",
            fontWeight: 600,
            marginBottom: "8px",
          }}
        >
          GUARDNET-AI / HUMAN REVIEW
        </div>

        <h1
          style={{
            margin: 0,
            fontSize: "34px",
            color: "#172b4d",
          }}
        >
          Human Review
        </h1>

        <p
          style={{
            color: "#718096",
          }}
        >
          Verifikasi hasil deteksi AI
          sebelum keputusan akhir.
        </p>
      </div>

      {message && (
        <div
          style={{
            background: "#eff6ff",
            color: "#1d4ed8",
            borderRadius: "12px",
            padding: "15px",
            marginBottom: "20px",
          }}
        >
          {message}
        </div>
      )}

      {loading ? (
        <div
          style={{
            background: "#fff",
            borderRadius: "18px",
            padding: "50px",
            textAlign: "center",
          }}
        >
          Loading pending reviews...
        </div>
      ) : cases.length === 0 ? (
        <div
          style={{
            background: "#fff",
            borderRadius: "18px",
            padding: "60px",
            textAlign: "center",
          }}
        >
          <h2>
            Tidak ada case yang menunggu
            review.
          </h2>

          <p
            style={{
              color: "#718096",
            }}
          >
            Semua case sudah diverifikasi.
          </p>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(320px, 1fr))",
            gap: "20px",
          }}
        >
          {cases.map((item) => (
            <div
              key={item.case_id}
              style={{
                background: "#fff",
                borderRadius: "18px",
                padding: "24px",
                border:
                  "1px solid #e5eaf2",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  marginBottom: "18px",
                }}
              >
                <strong>
                  {item.filename ||
                    "Unknown File"}
                </strong>

                <span
                  style={{
                    background: "#fee2e2",
                    color: "#dc2626",
                    padding:
                      "5px 10px",
                    borderRadius: "8px",
                    fontSize: "12px",
                    fontWeight: 800,
                  }}
                >
                  C2
                </span>
              </div>

              <div
                style={{
                  marginBottom: "15px",
                  color: "#64748b",
                  fontSize: "14px",
                }}
              >
                Risk Score:{" "}
                <strong>
                  {(
                    (item.classification
                      ?.risk_score ||
                      0) * 100
                  ).toFixed(1)}
                  %
                </strong>
              </div>

              <div
                style={{
                  marginBottom: "20px",
                  color: "#64748b",
                  fontSize: "14px",
                }}
              >
                Status:{" "}
                <strong>
                  {item.status}
                </strong>
              </div>

              <button
                onClick={() =>
                  setSelectedCase(
                    item
                  )
                }
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "none",
                  borderRadius: "10px",
                  background:
                    "#2563eb",
                  color: "#fff",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Review Case
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedCase && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background:
              "rgba(15,23,42,0.55)",
            display: "flex",
            alignItems: "center",
            justifyContent:
              "center",
            padding: "20px",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: "20px",
              padding: "30px",
              width: "100%",
              maxWidth: "600px",
            }}
          >
            <h2>
              Review Case
            </h2>

            <p
              style={{
                color: "#64748b",
              }}
            >
              {selectedCase.filename}
            </p>

            <div
              style={{
                background:
                  "#f8fafc",
                borderRadius: "12px",
                padding: "15px",
                margin:
                  "20px 0",
              }}
            >
              <strong>
                AI Classification:
              </strong>

              <div>
                C2 — HIGH RISK
              </div>

              <div>
                Risk:{" "}
                {(
                  selectedCase
                    .classification
                    ?.risk_score *
                    100
                ).toFixed(1)}
                %
              </div>
            </div>

            <textarea
              value={notes}
              onChange={(e) =>
                setNotes(
                  e.target.value
                )
              }
              placeholder="Masukkan catatan reviewer..."
              style={{
                width: "100%",
                minHeight: "120px",
                boxSizing:
                  "border-box",
                border:
                  "1px solid #dbe2ec",
                borderRadius: "12px",
                padding: "14px",
                resize: "vertical",
              }}
            />

            <div
              style={{
                display: "flex",
                gap: "10px",
                marginTop: "20px",
              }}
            >
              <button
                onClick={() =>
                  reviewCase(
                    "approve"
                  )
                }
                style={{
                  flex: 1,
                  padding: "13px",
                  border: "none",
                  borderRadius: "10px",
                  background:
                    "#16a34a",
                  color: "#fff",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Approve
              </button>

              <button
                onClick={() =>
                  reviewCase(
                    "reject"
                  )
                }
                style={{
                  flex: 1,
                  padding: "13px",
                  border: "none",
                  borderRadius: "10px",
                  background:
                    "#dc2626",
                  color: "#fff",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Reject
              </button>

              <button
                onClick={() =>
                  setSelectedCase(
                    null
                  )
                }
                style={{
                  flex: 1,
                  padding: "13px",
                  border: "1px solid #dbe2ec",
                  borderRadius: "10px",
                  background:
                    "#fff",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default HumanReview;