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
        padding: "0.5rem 1rem",
        backgroundColor: listening ? "red" : "#4CAF50",
        color: "white",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
        marginRight: "1rem",
      }}
    >
      {listening ? "Listening..." : "🎤 Speak"}
    </button>
  );
}
