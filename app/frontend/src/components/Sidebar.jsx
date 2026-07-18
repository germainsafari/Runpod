import { PlusIcon, TrashIcon } from "./Icons";

export default function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect,
  onDelete,
  configured,
  onOpenSettings,
  mobileOpen,
  onCloseMobile,
}) {
  return (
    <>
      {mobileOpen ? <button className="sidebar-overlay" onClick={onCloseMobile} aria-label="Close menu" /> : null}
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-mark">✦</div>
            <div>
              <h1>Flux Studio</h1>
              <p>RunPod · FLUX.1-dev</p>
            </div>
          </div>
          <button className="primary-button new-chat" onClick={onNewChat}>
            <PlusIcon />
            New chat
          </button>
        </div>

        <div className="conversation-list">
          <p className="section-label">Recent</p>
          {conversations.length === 0 ? (
            <p className="empty-list">No conversations yet</p>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`conversation-item ${conversation.id === activeId ? "active" : ""}`}
              >
                <button className="conversation-button" onClick={() => onSelect(conversation.id)}>
                  <span>{conversation.title}</span>
                </button>
                <button
                  className="icon-button danger"
                  onClick={() => onDelete(conversation.id)}
                  aria-label="Delete conversation"
                >
                  <TrashIcon />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <button className="ghost-button" onClick={onOpenSettings}>
            Settings
          </button>
          <div className={`status-pill ${configured ? "ok" : "warn"}`}>
            <span className="status-dot" />
            {configured ? "Endpoint ready" : "Configure API keys"}
          </div>
        </div>
      </aside>
    </>
  );
}
