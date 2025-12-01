export default function ChatBubble({ message, sender }) {
  const isUser = sender === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "0.5rem"
      }}
    >
      <div
        style={{
          backgroundColor: isUser ? "#007bff" : "#e5e5ea",
          color: isUser ? "white" : "black",
          padding: "0.5rem 1rem",
          borderRadius: "20px",
          maxWidth: "70%"
        }}
      >
        {message}
      </div>
    </div>
  );
}
