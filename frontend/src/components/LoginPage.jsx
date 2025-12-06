import React from "react";

export default function LoginPage() {
  const handleLogin = () => {
    window.open("https://vocalagentapi.onrender.com/auth/login/google", "_self");

  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "60vh",
      padding: "2rem"
    }}>
      <div style={{
        backgroundColor: "white",
        padding: "3rem 2.5rem",
        borderRadius: "20px",
        boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
        textAlign: "center",
        maxWidth: "450px",
        width: "100%",
        animation: "fadeIn 0.5s ease-in"
      }}>
        <div style={{
          fontSize: "4rem",
          marginBottom: "1.5rem"
        }}>
          🤖
        </div>
        <h2 style={{
          fontSize: "2rem",
          marginBottom: "1rem",
          color: "#1a1a1a",
          fontWeight: "700"
        }}>
          Welcome to Vocal Agent
        </h2>
        <p style={{
          color: "#666",
          fontSize: "1.05rem",
          marginBottom: "2.5rem",
          lineHeight: "1.6"
        }}>
          Your AI-powered assistant for Google Workspace. Control Gmail, Calendar, Drive, Docs, and more with just your voice.
        </p>
        <button
          onClick={handleLogin}
          style={{
            padding: "1rem 2.5rem",
            fontSize: "1.1rem",
            fontWeight: "600",
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            borderRadius: "12px",
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(25, 118, 210, 0.3)",
            transition: "all 0.2s",
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            margin: "0 auto"
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "#1565c0";
            e.target.style.transform = "translateY(-2px)";
            e.target.style.boxShadow = "0 6px 16px rgba(25, 118, 210, 0.4)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "#1976d2";
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow = "0 4px 12px rgba(25, 118, 210, 0.3)";
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Login with Google
        </button>
        <p style={{
          marginTop: "1.5rem",
          fontSize: "0.85rem",
          color: "#999"
        }}>
          Secure authentication powered by Google OAuth 2.0
        </p>
      </div>
    </div>
  );
}
