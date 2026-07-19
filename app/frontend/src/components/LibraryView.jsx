import { DownloadIcon } from "./Icons";
import { formatRelativeTime } from "../utils/storage";

function downloadImage(base64, prompt) {
  const link = document.createElement("a");
  link.href = `data:image/png;base64,${base64}`;
  link.download = `${prompt.slice(0, 40).replace(/[^\w]+/g, "-") || "flux-image"}.png`;
  link.click();
}

export default function LibraryView({ items, onOpenChat }) {
  return (
    <div className="library-view">
      <header className="view-header">
        <div>
          <h2>Library</h2>
          <p>Every image you have generated, saved locally in this browser.</p>
        </div>
        <span className="view-badge">{items.length} images</span>
      </header>

      {items.length === 0 ? (
        <div className="library-empty">
          <h3>No images yet</h3>
          <p>Start a chat and your generated images will appear here automatically.</p>
        </div>
      ) : (
        <div className="library-grid">
          {items.map((item) => (
            <article key={item.id} className="library-card">
              <button
                type="button"
                className="library-image-button"
                onClick={() => onOpenChat(item.conversationId)}
              >
                <img
                  src={`data:image/png;base64,${item.imageBase64}`}
                  alt={item.prompt}
                  loading="lazy"
                />
              </button>
              <div className="library-card-body">
                <p className="library-prompt">{item.prompt}</p>
                <div className="library-meta">
                  <span>{item.conversationTitle}</span>
                  <span>{formatRelativeTime(item.createdAt)}</span>
                </div>
                <div className="library-actions">
                  <button
                    type="button"
                    className="ghost-button compact"
                    onClick={() => downloadImage(item.imageBase64, item.prompt)}
                  >
                    <DownloadIcon />
                    Download
                  </button>
                  <button
                    type="button"
                    className="ghost-button compact"
                    onClick={() => onOpenChat(item.conversationId)}
                  >
                    Open chat
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
