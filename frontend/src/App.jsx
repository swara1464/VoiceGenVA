import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "./axios"; // We MUST use the configured axios for credential handling

import LoginPage from "./components/LoginPage";
import Dashboard from "./components/Dashboard";
// We don't need echoTest from ./api as we use axios directly to /planner/run
import MicButton from "./components/MicButton";
import ChatBubble from "./components/ChatBubble";
import ApprovalModal from "./components/ApprovalModal"; // NEW: Import Modal component

function App() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  
  // NEW State for Approval Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [approvalProps, setApprovalProps] = useState({
    message: "",
    action: "",
    params: {}
  });

  const handleMicResult = (text) => {
    setInput(text);
  };
  
  // NEW: Function to handle approved action execution (calls /agent/execute)
  const handleExecute = async () => {
    const { action, params } = approvalProps;
    setIsModalOpen(false); // Close modal immediately
    
    // Add pending message for execution feedback
    setChatHistory(prev => [
      ...prev, 
      { message: `AGENT: Executing approved action: ${action}...\n(Check Console for API status)`, sender: "agent", pending: true }
    ]);

    try {
      // Call the new execution endpoint
      const res = await axios.post("/agent/execute", { action, params });
      
      // Get the response (e.g., Email successfully sent)
      const executionMessage = res.data.message || "Action completed.";

      // Find the pending message and replace it with the final result
      setChatHistory(prev => prev.map(chat => 
        chat.pending ? { message: executionMessage, sender: "agent", details: res.data.details } : chat
      ));

    } catch (err) {
      setChatHistory(prev => prev.map(chat => 
        chat.pending ? { message: "Error executing action ❌", sender: "agent" } : chat
      ));
      console.error("Execution failed:", err);
    }
  };

  // NEW: Function to handle rejected action
  const handleReject = () => {
    setIsModalOpen(false);
    setChatHistory(prev => [
      ...prev,
      { message: "AGENT: Action rejected. Task cancelled.", sender: "agent" }
    ]);
  };


  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    // Add user message to chat
    setChatHistory(prev => [...prev, { message: userMessage, sender: "user" }]);
    setInput(""); // clear input immediately

    try {
      // Send message to the planner route (which now returns structured response)
      const res = await axios.post("/planner/run", { prompt: userMessage });
      const data = res.data;

      // Handle structured response from backend
      if (data.response_type === "APPROVAL") {
        // Show approval modal
        setApprovalProps({
          message: data.message,
          action: data.action,
          params: data.params
        });
        setIsModalOpen(true);
      } else {
        // Handle RESULT, PLAN_ONLY, or ERROR response types
        setChatHistory(prev => [
          ...prev,
          { message: data.response, sender: "agent" }
        ]);
      }

    } catch (err) {
      setChatHistory(prev => [
        ...prev,
        { message: "Error connecting to backend or running planner ❌", sender: "agent" }
      ]);
      console.error(err);
    }
  };


  return (
    <BrowserRouter>
      <div style={{ padding: "2rem", fontFamily: "Arial" }}>
        <h1>Vocal Agent Test</h1>

        {/* Chat area */}
        <div
          style={{
            border: "1px solid #ccc",
            padding: "1rem",
            borderRadius: "8px",
            maxHeight: "300px",
            overflowY: "auto",
            marginBottom: "1rem"
          }}
        >
          {chatHistory.map((chat, idx) => (
            // Added check for chat.message to handle potential nulls
            chat.message ? <ChatBubble key={idx} message={chat.message} sender={chat.sender} /> : null
          ))}
        </div>

        {/* Input + Mic */}
        <div style={{ display: "flex", alignItems: "center", marginBottom: "2rem" }}>
          <MicButton onResult={handleMicResult} />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { // Added support for hitting Enter to send
              if (e.key === 'Enter') handleSend();
            }}
            placeholder="Type your command (e.g., 'Email HR the report')..."
            style={{ flex: 1, marginRight: "0.5rem", padding: "0.5rem" }}
          />
          <button onClick={handleSend} style={{ padding: "0.5rem 1rem" }}>
            Send
          </button>
        </div>
        
        {/* Approval Modal component */}
        <ApprovalModal
          isOpen={isModalOpen}
          message={approvalProps.message}
          onApprove={handleExecute}
          onReject={handleReject}
        />

        {/* Routes */}
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;