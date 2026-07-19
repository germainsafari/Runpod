const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "";

export function apiUrl(path) {
  return `${API_BASE}${path}`;
}

export async function fetchHealth() {
  const response = await fetch(apiUrl("/api/health"));
  return response.json();
}

export async function submitGeneration(prompt, settings) {
  const response = await fetch(apiUrl("/api/chat/submit"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, ...settings }),
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || "Failed to submit generation job");
  }
  return body;
}

export async function fetchJobStatus(jobId) {
  const response = await fetch(apiUrl(`/api/chat/status/${jobId}`));
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || "Failed to fetch job status");
  }
  return body;
}
