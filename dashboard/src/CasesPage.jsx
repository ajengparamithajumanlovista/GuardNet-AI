import React, { useEffect, useState } from "react";

function CasesPage({ apiBase, onBack }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");

  const loadCases = async () => {
    setLoading(true);

    try {
      const endpoints = [
        "/api/cases",
        "/cases",
        "/api/dashboard/cases",
      ];

      let found = [];

      for (const endpoint of endpoints) {
        try {
          const response = await fetch(
            `${apiBase}${endpoint}`
          );

          if (!response.ok) continue;

          const data =
            await response.json();

          if (Array.isArray(data)) {
            found = data;
            break;
          }

          if (Array.isArray(data?.cases)) {
            found = data.cases;
            break;
          }

          if (Array.isArray(data?.items)) {
            found = data.items;
            break;
          }
        } catch {
          continue;
        }
      }

      setCases(found);
    } catch (error) {
      console.error(error);
      setCases([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  const getClassification = (item) => {
    return (
      item?.classification?.classification ||
      item?.classification ||
      item?.fusion?.classification ||
      "C0"
    );
  };

  const getRisk = (item) => {
    return Number(
      item?.classification?.risk_score ??
        item?.risk_score ??
        item?.fusion?.risk_score ??
        0
    );
  };

  const filteredCases =
    filter === "ALL"
      ? cases
      : cases.filter(
          (item) =>
            getClassification(item) ===
            filter
        );

  return (
    <div className="dashboard-page">

      <header className="page-header">

        <div>
          <button
            className="back-button"
            onClick={onBack}
          >
            ← Dashboard
          </button>

          <div className="breadcrumb">
            GUARDNET-AI
            <span>/</span>
            Cases
          </div>

          <h1>
            Detected Cases
          </h1>

          <p>
            Monitoring and investigation
            results.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={loadCases}
        >
          ↻ Refresh
        </button>

      </header>

      <section className="case-filter-bar">

        {["ALL", "C0", "C1", "C2"].map(
          (item) => (
            <button
              key={item}
              className={
                filter === item
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={() =>
                setFilter(item)
              }
            >
              {item === "ALL"
                ? "All Cases"
                : item}
            </button>
          )
        )}

      </section>

      <section className="cases-table-panel">

        {loading ? (
          <div className="empty-state">
            Loading cases...
          </div>
        ) : filteredCases.length ===
          0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ◌
            </div>

            <strong>
              No cases found
            </strong>

            <span>
              Belum ada data case untuk
              filter ini.
            </span>
          </div>
        ) : (
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
                    RISK SCORE
                  </th>

                  <th>
                    STATUS
                  </th>

                  <th>
                    DATE
                  </th>
                </tr>
              </thead>

              <tbody>

                {filteredCases
                  .slice()
                  .reverse()
                  .map(
                    (item, index) => {
                      const classification =
                        getClassification(
                          item
                        );

                      const risk =
                        getRisk(item);

                      return (
                        <tr
                          key={
                            item.case_id ||
                            item.id ||
                            index
                          }
                        >
                          <td>
                            <strong>
                              {item.case_id ||
                                item.filename ||
                                `CASE-${index + 1}`}
                            </strong>
                          </td>

                          <td>
                            <span
                              className={`mini-class ${classification.toLowerCase()}`}
                            >
                              {classification}
                            </span>
                          </td>

                          <td>
                            {(risk * 100).toFixed(
                              1
                            )}
                            %
                          </td>

                          <td>
                            {item.status ||
                              item.cyber_security
                                ?.severity ||
                              "ANALYZED"}
                          </td>

                          <td>
                            {item.created_at
                              ? new Date(
                                  item.created_at
                                ).toLocaleString(
                                  "id-ID"
                                )
                              : "-"}
                          </td>
                        </tr>
                      );
                    }
                  )}

              </tbody>

            </table>

          </div>
        )}

      </section>

    </div>
  );
}

export default CasesPage;