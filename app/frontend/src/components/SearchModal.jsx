import { useEffect, useRef, useState } from "react";
import { CloseIcon, SearchIcon } from "./Icons";
import { formatRelativeTime } from "../utils/storage";

export default function SearchModal({ conversations, onSelect, onClose }) {
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const normalized = query.trim().toLowerCase();
  const results = normalized
    ? conversations
        .filter((conversation) => {
          const titleMatch = conversation.title.toLowerCase().includes(normalized);
          const messageMatch = conversation.messages.some((message) => {
            const text = message.content || message.prompt || "";
            return text.toLowerCase().includes(normalized);
          });
          return titleMatch || messageMatch;
        })
        .sort((a, b) => b.updatedAt - a.updatedAt)
    : conversations.sort((a, b) => b.updatedAt - a.updatedAt).slice(0, 8);

  useEffect(() => {
    function handleKey(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop search-backdrop" onClick={onClose}>
      <div className="search-modal" onClick={(event) => event.stopPropagation()}>
        <div className="search-input-row">
          <SearchIcon />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search chats…"
          />
          <button type="button" className="icon-button subtle" onClick={onClose} aria-label="Close search">
            <CloseIcon />
          </button>
        </div>
        <div className="search-results">
          {results.length === 0 ? (
            <p className="empty-list">No chats found</p>
          ) : (
            results.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                className="search-result"
                onClick={() => {
                  onSelect(conversation.id);
                  onClose();
                }}
              >
                <span className="search-result-title">{conversation.title}</span>
                <span className="search-result-meta">{formatRelativeTime(conversation.updatedAt)}</span>
              </button>
            ))
          )}
        </div>
        <p className="search-hint">Tip: press Ctrl+K anytime to search</p>
      </div>
    </div>
  );
}
