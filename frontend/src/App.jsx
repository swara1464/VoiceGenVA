import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./components/LoginPage";
import Dashboard from "./components/Dashboard";
import { echoTest } from "./api";
import MicButton from "./components/MicButton";
import ChatBubble from "./components/ChatBubble";

function App() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleMicResult = (text) => {
    setInput(text);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    setChatHistory([...chatHistory, { message: input, sender: "user" }]);

    try {
      const res = await echoTest(input);

      // Add agent response to chat
      setChatHistory(prev => [
        ...prev,
        { message: JSON.stringify(res), sender: "agent" }
      ]);
    } catch (err) {
      setChatHistory(prev => [
        ...prev,
        { message: "Error connecting to backend ❌", sender: "agent" }
      ]);
      console.error(err);
    }

    setInput(""); // clear input after sending
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
            <ChatBubble key={idx} message={chat.message} sender={chat.sender} />
          ))}
        </div>

        {/* Input + Mic */}
        <div style={{ display: "flex", alignItems: "center", marginBottom: "2rem" }}>
          <MicButton onResult={handleMicResult} />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            style={{ flex: 1, marginRight: "0.5rem", padding: "0.5rem" }}
          />
          <button onClick={handleSend} style={{ padding: "0.5rem 1rem" }}>
            Send
          </button>
        </div>

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
import axios from "./axios"; // or wherever you handle API calls

const handleSend = async () => {
  if (!input.trim()) return;

  // Add user message
  setChatHistory([...chatHistory, { message: input, sender: "user" }]);

  try {
    const res = await axios.post("/planner/run", { prompt: input });
    setChatHistory(prev => [
      ...prev,
      { message: res.data.response, sender: "agent" }
    ]);
  } catch (err) {
    setChatHistory(prev => [
      ...prev,
      { message: "Error connecting to backend ❌", sender: "agent" }
    ]);
    console.error(err);
  }

  setInput("");
};
