import { DownloadIcon } from "./Icons";

function downloadImage(base64, prompt) {
  const link = document.createElement("a");
  link.href = `data:image/png;base64,${base64}`;
  link.download = `${prompt.slice(0, 40).replace(/[^\w]+/g, "-") || "flux-image"}.png`;
  link.click();
}

export default function ChatMessage({ message, onRetry }) {
  if (message.role === "user") {
    return (
      <article className="message user-message">
        <div className="message-inner">
          <p>{message.content}</p>
        </div>
      </article>
    );
  }

  if (message.status === "loading") {
    return (
      <article className="message assistant-message">
        <div className="assistant-avatar">F</div>
        <div className="message-inner assistant-card loading-card">
          <div className="typing-indicator">
            <span />
            <span />
            <span />
          </div>
          <p className="loading-text">{message.progress || "Starting GPU worker on RunPod…"}</p>
        </div>
      </article>
    );
  }

  if (message.status === "error") {
    return (
      <article className="message assistant-message">
        <div className="assistant-avatar">F</div>
        <div className="message-inner assistant-card error-card">
          <p>{message.content}</p>
          {message.retryPrompt ? (
            <button className="ghost-button" onClick={() => onRetry(message.retryPrompt)}>
              Try again
            </button>
          ) : null}
        </div>
      </article>
    );
  }

  return (
    <article className="message assistant-message">
      <div className="assistant-avatar">F</div>
      <div className="message-inner assistant-card">
        <img
          src={`data:image/png;base64,${message.imageBase64}`}
          alt={message.prompt}
          className="generated-image"
          loading="lazy"
        />
        <div className="message-actions">
          <button
            className="ghost-button"
            onClick={() => downloadImage(message.imageBase64, message.prompt)}
          >
            <DownloadIcon />
            Download PNG
          </button>
          {message.executionTimeMs ? (
            <span className="meta">
              Rendered in {(message.executionTimeMs / 1000).toFixed(1)}s
              {message.jobId ? ` · Job ${message.jobId.slice(0, 8)}` : ""}
            </span>
          ) : null}
        </div>
      </div>
    </article>
  );
}
