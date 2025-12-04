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
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>Voice Command Interface</h2>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={isTTSEnabled}
              onChange={(e) => setIsTTSEnabled(e.target.checked)}
            />
            <span>Voice Response</span>
          </label>
          <Link to="/history" style={{ padding: "0.5rem 1rem", backgroundColor: "#007bff", color: "white", textDecoration: "none", borderRadius: "5px" }}>
            History
          </Link>
          <Link to="/dashboard" style={{ padding: "0.5rem 1rem", backgroundColor: "#28a745", color: "white", textDecoration: "none", borderRadius: "5px" }}>
            Profile
          </Link>
        </div>
      </div>

      <div
        style={{
          border: "1px solid #ddd",
          padding: "1.5rem",
          borderRadius: "12px",
          minHeight: "400px",
          maxHeight: "500px",
          overflowY: "auto",
          marginBottom: "1.5rem",
          backgroundColor: "#f9f9f9",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
        }}
      >
        {chatHistory.length === 0 ? (
          <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
            <p style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Welcome to Vocal Agent</p>
            <p>Try commands like:</p>
            <ul style={{ listStyle: "none", padding: 0, lineHeight: "2" }}>
              <li>"Search Drive for project files"</li>
              <li>"Create a task to complete the report"</li>
              <li>"Schedule a meeting tomorrow at 2 PM"</li>
              <li>"List my contacts"</li>
            </ul>
          </div>
        ) : (
          chatHistory.map((chat, idx) => (
            chat.message ? <ChatBubble key={idx} message={chat.message} sender={chat.sender} /> : null
          ))
        )}
      </div>

      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
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
            padding: "0.75rem",
            fontSize: "1rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            outline: "none"
          }}
        />
        <button
          onClick={handleSend}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: "bold"
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
        fontFamily: "system-ui, -apple-system, sans-serif",
        backgroundColor: "#f5f5f5"
      }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <h1 style={{ marginBottom: "2rem", color: "#333" }}>Vocal Agent</h1>

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