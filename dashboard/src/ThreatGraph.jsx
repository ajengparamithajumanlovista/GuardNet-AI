import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function ThreatGraph() {
  const [graph, setGraph] = useState({
    nodes: [],
    links: [],
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadGraph = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE}/api/threat-graph`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      setGraph({
        nodes: Array.isArray(data.nodes)
          ? data.nodes
          : [],
        links: Array.isArray(data.links)
          ? data.links
          : [],
      });
    } catch (err) {
      console.error(
        "Threat Graph Error:",
        err
      );

      setError(
        "Threat Graph gagal mengambil data dari backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "36px",
        boxSizing: "border-box",
      }}
    >
      {/* HEADER */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "30px",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "13px",
              color: "#718096",
              marginBottom: "8px",
              fontWeight: 600,
            }}
          >
            GUARDNET-AI / THREAT GRAPH
          </div>

          <h1
            style={{
              margin: 0,
              color: "#13233f",
              fontSize: "34px",
              fontWeight: 800,
            }}
          >
            Threat Graph
          </h1>

          <p
            style={{
              marginTop: "8px",
              color: "#718096",
              fontSize: "15px",
            }}
          >
            Visualisasi hubungan antar kasus
            dan indikator ancaman digital.
          </p>
        </div>

        <button
          onClick={loadGraph}
          style={{
            border: "1px solid #dce3ef",
            background: "#ffffff",
            borderRadius: "12px",
            padding: "12px 20px",
            cursor: "pointer",
            fontWeight: 700,
            color: "#20314f",
          }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* STATUS */}

      <div
        style={{
          background: "#ffffff",
          border: "1px solid #e4e9f2",
          borderRadius: "18px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "30px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "13px",
                color: "#718096",
              }}
            >
              Total Nodes
            </div>

            <div
              style={{
                fontSize: "28px",
                fontWeight: 800,
                color: "#172b4d",
              }}
            >
              {graph.nodes.length}
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "13px",
                color: "#718096",
              }}
            >
              Relationships
            </div>

            <div
              style={{
                fontSize: "28px",
                fontWeight: 800,
                color: "#172b4d",
              }}
            >
              {graph.links.length}
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "13px",
                color: "#718096",
              }}
            >
              Backend
            </div>

            <div
              style={{
                fontSize: "16px",
                fontWeight: 700,
                color: "#16a34a",
                marginTop: "8px",
              }}
            >
              ● Connected
            </div>
          </div>
        </div>
      </div>

      {/* ERROR */}

      {error && (
        <div
          style={{
            background: "#fff1f2",
            border: "1px solid #fecdd3",
            color: "#be123c",
            borderRadius: "14px",
            padding: "18px",
            marginBottom: "24px",
          }}
        >
          {error}
        </div>
      )}

      {/* LOADING */}

      {loading && (
        <div
          style={{
            background: "#ffffff",
            borderRadius: "18px",
            padding: "60px",
            textAlign: "center",
            color: "#718096",
          }}
        >
          Loading Threat Graph...
        </div>
      )}

      {/* GRAPH */}

      {!loading && !error && (
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e4e9f2",
            borderRadius: "20px",
            padding: "30px",
            minHeight: "450px",
          }}
        >
          <h2
            style={{
              marginTop: 0,
              color: "#172b4d",
              fontSize: "20px",
            }}
          >
            Digital Threat Network
          </h2>

          {graph.nodes.length === 0 ? (
            <div
              style={{
                padding: "80px 20px",
                textAlign: "center",
                color: "#718096",
              }}
            >
              <div
                style={{
                  fontSize: "42px",
                  marginBottom: "16px",
                }}
              >
                ◉
              </div>

              <h3
                style={{
                  color: "#334155",
                  marginBottom: "8px",
                }}
              >
                No threat nodes detected
              </h3>

              <p>
                Belum terdapat node ancaman
                yang tersedia.
              </p>
            </div>
          ) : (
            <>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(240px, 1fr))",
                  gap: "18px",
                  marginTop: "25px",
                }}
              >
                {graph.nodes.map(
                  (node, index) => (
                    <div
                      key={
                        node.id ||
                        `node-${index}`
                      }
                      style={{
                        border:
                          "1px solid #e1e7f0",
                        borderRadius: "16px",
                        padding: "20px",
                        background:
                          "#f9fbff",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems:
                            "center",
                          gap: "12px",
                          marginBottom:
                            "15px",
                        }}
                      >
                        <div
                          style={{
                            width: "42px",
                            height: "42px",
                            borderRadius:
                              "12px",
                            background:
                              "#eaf2ff",
                            display: "flex",
                            alignItems:
                              "center",
                            justifyContent:
                              "center",
                            color:
                              "#2563eb",
                            fontSize:
                              "20px",
                          }}
                        >
                          ●
                        </div>

                        <div>
                          <div
                            style={{
                              fontWeight:
                                800,
                              color:
                                "#172b4d",
                            }}
                          >
                            {node.type ||
                              "Unknown"}
                          </div>

                          <div
                            style={{
                              fontSize:
                                "12px",
                              color:
                                "#718096",
                            }}
                          >
                            Threat Node
                          </div>
                        </div>
                      </div>

                      <div
                        style={{
                          fontSize:
                            "12px",
                          color:
                            "#64748b",
                            wordBreak:
                            "break-all",
                        }}
                      >
                        {node.value ||
                          node.id ||
                          "Unknown"}
                      </div>
                    </div>
                  )
                )}
              </div>

              {/* RELATIONSHIP */}

              <div
                style={{
                  marginTop: "30px",
                  borderTop:
                    "1px solid #e5eaf2",
                  paddingTop: "25px",
                }}
              >
                <h3
                  style={{
                    color: "#172b4d",
                  }}
                >
                  Relationships
                </h3>

                {graph.links.length ===
                0 ? (
                  <div
                    style={{
                      background:
                        "#f8fafc",
                      borderRadius:
                        "12px",
                      padding: "20px",
                      color:
                        "#64748b",
                    }}
                  >
                    No shared indicators
                    detected between the
                    current cases.
                  </div>
                ) : (
                  <div>
                    {graph.links.map(
                      (
                        link,
                        index
                      ) => (
                        <div
                          key={
                            index
                          }
                          style={{
                            padding:
                              "12px",
                            borderBottom:
                              "1px solid #edf0f5",
                          }}
                        >
                          {link.source} →
                          {link.target}
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default ThreatGraph;