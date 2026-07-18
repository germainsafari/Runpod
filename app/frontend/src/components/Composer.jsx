import { SendIcon, SettingsIcon } from "./Icons";

export default function Composer({
  prompt,
  onPromptChange,
  onSubmit,
  isGenerating,
  onOpenSettings,
}) {
  return (
    <div className="composer-shell">
      <form className="composer" onSubmit={onSubmit}>
        <div className="composer-box">
          <textarea
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            placeholder="Describe the image you want to create…"
            rows={1}
            disabled={isGenerating}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                onSubmit(event);
              }
            }}
          />
          <div className="composer-actions">
            <button type="button" className="icon-button" onClick={onOpenSettings} aria-label="Settings">
              <SettingsIcon />
            </button>
            <button type="submit" className="send-button" disabled={isGenerating || !prompt.trim()}>
              <SendIcon />
            </button>
          </div>
        </div>
        <p className="composer-hint">Enter to send · Shift+Enter for a new line · Powered by RunPod Serverless</p>
      </form>
    </div>
  );
}
