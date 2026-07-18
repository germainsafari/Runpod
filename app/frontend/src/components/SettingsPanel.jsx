export default function SettingsPanel({ settings, onChange, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="settings-panel" onClick={(event) => event.stopPropagation()}>
        <header>
          <h3>Generation settings</h3>
          <button className="icon-button" onClick={onClose} aria-label="Close settings">
            ×
          </button>
        </header>

        <label>
          Inference steps
          <input
            type="range"
            min="10"
            max="50"
            value={settings.num_inference_steps}
            onChange={(event) =>
              onChange({ ...settings, num_inference_steps: Number(event.target.value) })
            }
          />
          <span>{settings.num_inference_steps}</span>
        </label>

        <label>
          Guidance scale
          <input
            type="range"
            min="1"
            max="10"
            step="0.5"
            value={settings.guidance_scale}
            onChange={(event) =>
              onChange({ ...settings, guidance_scale: Number(event.target.value) })
            }
          />
          <span>{settings.guidance_scale}</span>
        </label>

        <div className="settings-grid">
          <label>
            Width
            <select
              value={settings.width}
              onChange={(event) => onChange({ ...settings, width: Number(event.target.value) })}
            >
              <option value={512}>512</option>
              <option value={768}>768</option>
              <option value={1024}>1024</option>
            </select>
          </label>
          <label>
            Height
            <select
              value={settings.height}
              onChange={(event) => onChange({ ...settings, height: Number(event.target.value) })}
            >
              <option value={512}>512</option>
              <option value={768}>768</option>
              <option value={1024}>1024</option>
            </select>
          </label>
        </div>

        <label>
          Seed (optional)
          <input
            type="number"
            placeholder="Random"
            value={settings.seed ?? ""}
            onChange={(event) =>
              onChange({
                ...settings,
                seed: event.target.value ? Number(event.target.value) : null,
              })
            }
          />
        </label>
      </div>
    </div>
  );
}
