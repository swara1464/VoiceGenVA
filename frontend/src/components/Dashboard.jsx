import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "../axios";

export default function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    axios.get("/auth/me", { withCredentials: true })
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  const handleLogout = async () => {
    try {
      await axios.get("/auth/logout", { withCredentials: true });
      setUser(null);
      window.location.href = "/";
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  if (!user) return (
    <div style={{ textAlign: "center", padding: "3rem" }}>
      <p>Checking login...</p>
    </div>
  );

  return (
    <div style={{
      maxWidth: "600px",
      margin: "0 auto",
      padding: "2rem",
      backgroundColor: "white",
      borderRadius: "12px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
    }}>
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <img
          src={user.picture}
          alt="Profile"
          width={80}
          style={{ borderRadius: "50%", marginBottom: "1rem", boxShadow: "0 2px 4px rgba(0,0,0,0.2)" }}
        />
        <h2 style={{ margin: "0.5rem 0" }}>Welcome, {user.name}</h2>
        <p style={{ color: "#666", margin: "0.5rem 0" }}>{user.email}</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "2rem" }}>
        <Link
          to="/agent"
          style={{
            padding: "1rem",
            backgroundColor: "#007bff",
            color: "white",
            textDecoration: "none",
            borderRadius: "8px",
            textAlign: "center",
            fontWeight: "bold"
          }}
        >
          Open Voice Agent
        </Link>

        <Link
          to="/history"
          style={{
            padding: "1rem",
            backgroundColor: "#28a745",
            color: "white",
            textDecoration: "none",
            borderRadius: "8px",
            textAlign: "center",
            fontWeight: "bold"
          }}
        >
          View Execution History
        </Link>

        <button
          onClick={handleLogout}
          style={{
            padding: "1rem",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: "bold",
            fontSize: "1rem"
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}
