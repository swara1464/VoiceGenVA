// frontend/src/components/Dashboard.jsx
import { useEffect, useState } from "react";
import axios from "../axios";

export default function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Get current user info from backend
    axios.get("/auth/me", { withCredentials: true })
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  const handleLogout = async () => {
    try {
      await axios.get("/auth/logout", { withCredentials: true });
      setUser(null); // clears user info
      window.location.href = "/"; // redirect to login page
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  if (!user) return <p>Checking login...</p>;

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Welcome, {user.name} 👋</h2>
      <img
        src={user.picture}
        alt="Profile"
        width={60}
        style={{ borderRadius: "50%", marginBottom: "1rem" }}
      />
      <p>Email: {user.email}</p>

      <button
        onClick={handleLogout}
        style={{ padding: "0.5rem 1rem", marginTop: "1rem" }}
      >
        Logout
      </button>
    </div>
  );
}
