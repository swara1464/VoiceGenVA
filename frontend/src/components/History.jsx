import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "../axios";

export default function History() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/logs");
      setLogs(response.data.logs || []);
      setLoading(false);
    } catch (err) {
      setError("Failed to load execution history");
      setLoading(false);
      console.error("Error fetching logs:", err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "SUCCESS":
        return "#4CAF50";
      case "FAILED":
        return "#f44336";
      case "ATTEMPTING":
        return "#FFC107";
      default:
        return "#9E9E9E";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "SUCCESS":
        return "✓";
      case "FAILED":
        return "✗";
      case "ATTEMPTING":
        return "⏳";
      default:
        return "○";
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Loading execution history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem", textAlign: "center", color: "#f44336" }}>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h2 style={{ margin: 0 }}>Execution History</h2>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={fetchLogs}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#4CAF50",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            Refresh
          </button>
          <Link
            to="/agent"
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#007bff",
              color: "white",
              textDecoration: "none",
              borderRadius: "5px",
              fontWeight: "bold",
              display: "inline-block"
            }}
          >
            Back to Agent
          </Link>
        </div>
      </div>

      {logs.length === 0 ? (
        <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
          <p>No execution history yet. Try running some commands!</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {logs.map((log) => (
            <div
              key={log.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "1rem",
                backgroundColor: "#f9f9f9",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span
                    style={{
                      display: "inline-block",
                      width: "24px",
                      height: "24px",
                      borderRadius: "50%",
                      backgroundColor: getStatusColor(log.status),
                      color: "white",
                      textAlign: "center",
                      lineHeight: "24px",
                      fontWeight: "bold"
                    }}
                  >
                    {getStatusIcon(log.status)}
                  </span>
                  <strong>{log.action}</strong>
                </div>
                <span style={{ fontSize: "0.85rem", color: "#666" }}>
                  {new Date(log.timestamp).toLocaleString()}
                </span>
              </div>

              <div style={{ marginLeft: "2rem" }}>
                <div
                  style={{
                    display: "inline-block",
                    padding: "0.25rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.85rem",
                    backgroundColor: getStatusColor(log.status),
                    color: "white",
                    marginBottom: "0.5rem"
                  }}
                >
                  {log.status}
                </div>

                {log.details && (
                  <details style={{ marginTop: "0.5rem" }}>
                    <summary style={{ cursor: "pointer", color: "#007bff" }}>
                      View Details
                    </summary>
                    <pre
                      style={{
                        marginTop: "0.5rem",
                        padding: "0.5rem",
                        backgroundColor: "#fff",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        fontSize: "0.85rem",
                        overflow: "auto",
                        maxHeight: "200px"
                      }}
                    >
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
