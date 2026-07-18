const STARTER_PROMPTS = [
  {
    title: "Landscape",
    prompt: "A serene mountain landscape at golden hour, ultra detailed, cinematic",
  },
  {
    title: "Sci-fi city",
    prompt: "A futuristic city with flying cars at night, neon reflections, cyberpunk",
  },
  {
    title: "Portrait",
    prompt: "Studio portrait of a creative professional, soft lighting, editorial style",
  },
  {
    title: "Product",
    prompt: "Minimal product photo of a smartwatch on marble, premium advertising shot",
  },
];

export default function EmptyState({ onSelectPrompt }) {
  return (
    <div className="empty-state">
      <div className="empty-badge">RunPod Serverless · FLUX.1-dev</div>
      <h2>Turn prompts into images</h2>
      <p>
        A ChatGPT-style experience for AI image generation. Describe what you want to see and
        FLUX.1-dev renders it on RunPod GPU workers.
      </p>
      <div className="starter-grid">
        {STARTER_PROMPTS.map((item) => (
          <button key={item.title} className="starter-card" onClick={() => onSelectPrompt(item.prompt)}>
            <span className="starter-title">{item.title}</span>
            <span className="starter-copy">{item.prompt}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
