import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "./axios";

import LoginPage from "./components/LoginPage";
import Dashboard from "./components/Dashboard";
import History from "./components/History";
import MicButton from "./components/MicButton";
import ChatBubble from "./components/ChatBubble";
import ApprovalModal from "./components/ApprovalModal";

function App() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [approvalProps, setApprovalProps] = useState({
    message: "",
    action: "",
    params: {}
  });
  const [isTTSEnabled, setIsTTSEnabled] = useState(true);

  const speakText = (text) => {
    if (!isTTSEnabled || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    window.speechSynthesis.speak(utterance);
  };

  const handleMicResult = (text) => {
    setInput(text);
  };
  
  const handleExecute = async () => {
    const { action, params } = approvalProps;
    setIsModalOpen(false);

    const executingMessage = `Executing approved action: ${action}...`;
    setChatHistory(prev => [
      ...prev,
      { message: executingMessage, sender: "agent", pending: true }
    ]);

    try {
      const res = await axios.post("/agent/execute", { action, params });
      const executionMessage = res.data.message || "Action completed.";

      setChatHistory(prev => prev.map(chat =>
        chat.pending ? { message: executionMessage, sender: "agent", details: res.data.details } : chat
      ));

      speakText(executionMessage);

    } catch (err) {
      const errorMessage = "Error executing action";
      setChatHistory(prev => prev.map(chat =>
        chat.pending ? { message: errorMessage, sender: "agent" } : chat
      ));
      speakText(errorMessage);
      console.error("Execution failed:", err);
    }
  };

  const handleReject = () => {
    setIsModalOpen(false);
    const rejectMessage = "Action rejected. Task cancelled.";
    setChatHistory(prev => [
      ...prev,
      { message: rejectMessage, sender: "agent" }
    ]);
    speakText(rejectMessage);
  };


  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setChatHistory(prev => [...prev, { message: userMessage, sender: "user" }]);
    setInput("");

    try {
      const res = await axios.post("/planner/run", { prompt: userMessage });
      const data = res.data;

      if (data.response_type === "APPROVAL") {
        setApprovalProps({
          message: data.message,
          action: data.action,
          params: data.params
        });
        setIsModalOpen(true);
        speakText(data.message);
      } else {
        const agentMessage = data.response;
        setChatHistory(prev => [
          ...prev,
          { message: agentMessage, sender: "agent" }
        ]);
        speakText(agentMessage);
      }

    } catch (err) {
      const errorMessage = "Error connecting to backend or running planner";
      setChatHistory(prev => [
        ...prev,
        { message: errorMessage, sender: "agent" }
      ]);
      speakText(errorMessage);
      console.error(err);
    }
  };


  const VocalAgentHome = () => (
    <div>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "2rem",
        padding: "1rem",
        backgroundColor: "white",
        borderRadius: "12px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
      }}>
        <h2 style={{
          margin: 0,
          fontSize: "1.5rem",
          fontWeight: "600",
          color: "#1a1a1a",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem"
        }}>
          <span style={{ fontSize: "1.8rem" }}>🎙️</span>
          Voice Command Interface
        </h2>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <label style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            cursor: "pointer",
            padding: "0.5rem 0.75rem",
            backgroundColor: isTTSEnabled ? "#e8f5e9" : "#f5f5f5",
            borderRadius: "8px",
            transition: "all 0.2s"
          }}>
            <input
              type="checkbox"
              checked={isTTSEnabled}
              onChange={(e) => setIsTTSEnabled(e.target.checked)}
              style={{ cursor: "pointer" }}
            />
            <span style={{ fontSize: "0.9rem", fontWeight: "500" }}>🔊 Voice Response</span>
          </label>
          <Link to="/history" style={{
            padding: "0.6rem 1.2rem",
            backgroundColor: "#1976d2",
            color: "white",
            textDecoration: "none",
            borderRadius: "8px",
            fontWeight: "500",
            fontSize: "0.9rem",
            transition: "all 0.2s",
            boxShadow: "0 2px 4px rgba(25, 118, 210, 0.3)"
          }}>
            📋 History
          </Link>
          <Link to="/dashboard" style={{
            padding: "0.6rem 1.2rem",
            backgroundColor: "#2e7d32",
            color: "white",
            textDecoration: "none",
            borderRadius: "8px",
            fontWeight: "500",
            fontSize: "0.9rem",
            transition: "all 0.2s",
            boxShadow: "0 2px 4px rgba(46, 125, 50, 0.3)"
          }}>
            👤 Profile
          </Link>
        </div>
      </div>

      <div
        style={{
          border: "none",
          padding: "2rem",
          borderRadius: "16px",
          minHeight: "450px",
          maxHeight: "550px",
          overflowY: "auto",
          marginBottom: "1.5rem",
          backgroundColor: "white",
          boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
          backgroundImage: "linear-gradient(to bottom, #ffffff, #f8f9fa)"
        }}
      >
        {chatHistory.length === 0 ? (
          <div style={{ textAlign: "center", padding: "4rem 2rem", color: "#666" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🤖</div>
            <p style={{
              fontSize: "1.4rem",
              marginBottom: "1.5rem",
              fontWeight: "600",
              color: "#333"
            }}>
              Welcome to Vocal Agent
            </p>
            <p style={{
              fontSize: "1rem",
              marginBottom: "1.5rem",
              color: "#666"
            }}>
              Your AI-powered Google Workspace assistant
            </p>
            <div style={{
              backgroundColor: "#f0f7ff",
              padding: "1.5rem",
              borderRadius: "12px",
              border: "1px solid #bbdefb",
              maxWidth: "600px",
              margin: "0 auto"
            }}>
              <p style={{ fontWeight: "600", marginBottom: "1rem", color: "#1976d2" }}>Try these commands:</p>
              <ul style={{
                listStyle: "none",
                padding: 0,
                lineHeight: "2.2",
                textAlign: "left"
              }}>
                <li style={{ padding: "0.3rem 0" }}>📁 "Search Drive for project files"</li>
                <li style={{ padding: "0.3rem 0" }}>✅ "Create a task to complete the report"</li>
                <li style={{ padding: "0.3rem 0" }}>📅 "Schedule a meeting tomorrow at 2 PM"</li>
                <li style={{ padding: "0.3rem 0" }}>👥 "List my contacts"</li>
                <li style={{ padding: "0.3rem 0" }}>📝 "Create a note about the discussion"</li>
              </ul>
            </div>
          </div>
        ) : (
          chatHistory.map((chat, idx) => (
            chat.message ? <ChatBubble key={idx} message={chat.message} sender={chat.sender} /> : null
          ))
        )}
      </div>

      <div style={{
        display: "flex",
        gap: "0.75rem",
        alignItems: "center",
        padding: "1rem",
        backgroundColor: "white",
        borderRadius: "12px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
      }}>
        <MicButton onResult={handleMicResult} />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend();
          }}
          placeholder="Type or speak your command..."
          style={{
            flex: 1,
            padding: "0.9rem 1.2rem",
            fontSize: "1rem",
            border: "2px solid #e0e0e0",
            borderRadius: "10px",
            outline: "none",
            transition: "all 0.2s"
          }}
          onFocus={(e) => e.target.style.borderColor = "#1976d2"}
          onBlur={(e) => e.target.style.borderColor = "#e0e0e0"}
        />
        <button
          onClick={handleSend}
          style={{
            padding: "0.9rem 2rem",
            fontSize: "1rem",
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            borderRadius: "10px",
            cursor: "pointer",
            fontWeight: "600",
            transition: "all 0.2s",
            boxShadow: "0 2px 8px rgba(25, 118, 210, 0.3)"
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "#1565c0";
            e.target.style.transform = "translateY(-1px)";
            e.target.style.boxShadow = "0 4px 12px rgba(25, 118, 210, 0.4)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "#1976d2";
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow = "0 2px 8px rgba(25, 118, 210, 0.3)";
          }}
        >
          Send
        </button>
      </div>

      <ApprovalModal
        isOpen={isModalOpen}
        message={approvalProps.message}
        onApprove={handleExecute}
        onReject={handleReject}
      />
    </div>
  );

  return (
    <BrowserRouter>
      <div style={{
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
      }}>
        <div style={{
          maxWidth: "1200px",
          margin: "0 auto"
        }}>
          <div style={{
            marginBottom: "2rem",
            textAlign: "center"
          }}>
            <h1 style={{
              marginBottom: "0.5rem",
              color: "#ffffff",
              fontSize: "2.5rem",
              fontWeight: "700",
              textShadow: "0 2px 4px rgba(0,0,0,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "1rem"
            }}>
              <span style={{ fontSize: "2.5rem" }}>🤖</span>
              Vocal Agent
            </h1>
            <p style={{
              color: "rgba(255,255,255,0.9)",
              fontSize: "1.1rem",
              margin: 0,
              textShadow: "0 1px 2px rgba(0,0,0,0.2)"
            }}>
              AI-Powered Google Workspace Assistant
            </p>
          </div>

          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/agent" element={<VocalAgentHome />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;