import React from "react";

export default function LoginPage() {
  const handleLogin = () => {
    // Opens Google OAuth login URL
    window.open("http://localhost:5050/auth/login", "_self");
  };

  return (
    <div style={{ marginBottom: "1rem" }}>
      <h2>Login with Google</h2>
      <button onClick={handleLogin} style={{ padding: "0.5rem 1rem" }}>
        Login with Google
      </button>
    </div>
  );
}
