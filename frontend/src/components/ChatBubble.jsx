export default function ChatBubble({ message, sender }) {
  const isUser = sender === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "1rem",
        animation: "fadeIn 0.3s ease-in"
      }}
    >
      {!isUser && (
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "50%",
          backgroundColor: "#1976d2",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginRight: "0.75rem",
          fontSize: "1.2rem",
          flexShrink: 0
        }}>
          🤖
        </div>
      )}
      <div
        style={{
          backgroundColor: isUser ? "#1976d2" : "#f0f0f0",
          color: isUser ? "white" : "#1a1a1a",
          padding: "0.9rem 1.3rem",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          maxWidth: "70%",
          boxShadow: isUser
            ? "0 2px 8px rgba(25, 118, 210, 0.3)"
            : "0 2px 8px rgba(0,0,0,0.08)",
          fontSize: "0.95rem",
          lineHeight: "1.5",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word"
        }}
      >
        {message}
      </div>
      {isUser && (
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "50%",
          backgroundColor: "#2e7d32",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginLeft: "0.75rem",
          fontSize: "1.2rem",
          flexShrink: 0
        }}>
          👤
        </div>
      )}
    </div>
  );
}
