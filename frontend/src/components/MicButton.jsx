// frontend/src/components/MicButton.jsx
import { useState, useEffect } from "react";

export default function MicButton({ onResult }) {
  const [listening, setListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support the Web Speech API.");
      return;
    }

    const recog = new SpeechRecognition();
    recog.continuous = false; // Stop automatically after speech
    recog.interimResults = false;
    recog.lang = "en-US";

    // When speech is recognized
    recog.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript); // Pass text to parent component
    };

    // When recognition ends
    recog.onend = () => setListening(false);

    setRecognition(recog);
  }, [onResult]);

  const handleToggle = () => {
    if (!recognition) return;
    if (listening) {
      recognition.stop();
      setListening(false);
    } else {
      recognition.start();
      setListening(true);
    }
  };

  return (
    <button
      onClick={handleToggle}
      style={{
        padding: "0.9rem 1.5rem",
        backgroundColor: listening ? "#d32f2f" : "#2e7d32",
        color: "white",
        border: "none",
        borderRadius: "10px",
        cursor: "pointer",
        fontWeight: "600",
        fontSize: "1rem",
        transition: "all 0.2s",
        boxShadow: listening
          ? "0 0 20px rgba(211, 47, 47, 0.5)"
          : "0 2px 8px rgba(46, 125, 50, 0.3)",
        animation: listening ? "pulse 1.5s infinite" : "none"
      }}
      onMouseEnter={(e) => {
        if (!listening) {
          e.target.style.backgroundColor = "#1b5e20";
          e.target.style.transform = "translateY(-1px)";
          e.target.style.boxShadow = "0 4px 12px rgba(46, 125, 50, 0.4)";
        }
      }}
      onMouseLeave={(e) => {
        if (!listening) {
          e.target.style.backgroundColor = "#2e7d32";
          e.target.style.transform = "translateY(0)";
          e.target.style.boxShadow = "0 2px 8px rgba(46, 125, 50, 0.3)";
        }
      }}
    >
      {listening ? (
        <span>
          <span style={{ display: "inline-block", animation: "bounce 0.6s infinite" }}>🎤</span>
          {" "}Listening...
        </span>
      ) : (
        "🎤 Speak"
      )}
    </button>
  );
}
