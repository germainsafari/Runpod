import { useEffect, useRef } from "react";

export default function ContextMenu({ x, y, items, onClose }) {
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(event) {
      if (ref.current && !ref.current.contains(event.target)) {
        onClose();
      }
    }
    function handleKey(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("mousedown", handleClick);
    window.addEventListener("keydown", handleKey);
    return () => {
      window.removeEventListener("mousedown", handleClick);
      window.removeEventListener("keydown", handleKey);
    };
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="context-menu"
      style={{ top: y, left: x }}
      role="menu"
    >
      {items.map((item) =>
        item.separator ? (
          <div key={item.key} className="context-separator" />
        ) : (
          <button
            key={item.key}
            type="button"
            className={`context-item ${item.danger ? "danger" : ""}`}
            onClick={() => {
              item.onClick();
              onClose();
            }}
          >
            {item.icon ? <span className="context-icon">{item.icon}</span> : null}
            <span>{item.label}</span>
          </button>
        )
      )}
    </div>
  );
}
