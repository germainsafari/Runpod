import { useEffect, useRef, useState } from "react";
import ChatMessage from "./components/ChatMessage";
import Composer from "./components/Composer";
import EmptyState from "./components/EmptyState";
import SettingsPanel from "./components/SettingsPanel";
import Sidebar from "./components/Sidebar";
import { useConversations } from "./hooks/useConversations";

const DEFAULT_SETTINGS = {
  num_inference_steps: 20,
  guidance_scale: 3.5,
  width: 512,
  height: 512,
  seed: null,
};

const STATUS_LABELS = {
  IN_QUEUE: "Queued on RunPod…",
  IN_PROGRESS: "Generating on GPU…",
  COMPLETED: "Finalizing image…",
};

async function generateImage(prompt, settings, onProgress) {
  const submit = await fetch("/api/chat/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, ...settings }),
  });

  const submitBody = await submit.json();
  if (!submit.ok) {
    throw new Error(submitBody.detail || "Failed to submit generation job");
  }

  const jobId = submitBody.job_id;
  onProgress(STATUS_LABELS.IN_QUEUE);

  const deadline = Date.now() + 540_000;
  while (Date.now() < deadline) {
    const statusResponse = await fetch(`/api/chat/status/${jobId}`);
    const statusBody = await statusResponse.json();

    if (!statusResponse.ok) {
      throw new Error(statusBody.detail || "Failed to fetch job status");
    }

    const status = statusBody.status;
    if (STATUS_LABELS[status]) {
      onProgress(STATUS_LABELS[status]);
    }

    if (status === "COMPLETED") {
      if (!statusBody.image_base64) {
        throw new Error("RunPod completed without returning an image");
      }
      return {
        image_base64: statusBody.image_base64,
        job_id: jobId,
        execution_time_ms: statusBody.execution_time_ms,
      };
    }

    if (["FAILED", "CANCELLED", "TIMED_OUT"].includes(status)) {
      throw new Error(statusBody.error || `Job ${status.toLowerCase()}`);
    }

    await new Promise((resolve) => setTimeout(resolve, 2000));
  }

  throw new Error("Generation timed out after 9 minutes");
}

export default function App() {
  const {
    conversations,
    activeConversation,
    activeId,
    startNewChat,
    selectConversation,
    deleteConversation,
    updateMessages,
  } = useConversations();

  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [health, setHealth] = useState(null);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const bottomRef = useRef(null);

  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "error" }));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isGenerating]);

  async function runGeneration(rawPrompt) {
    const trimmed = rawPrompt.trim();
    if (!trimmed || isGenerating) return;

    setPrompt("");
    setIsGenerating(true);
    setMobileOpen(false);

    const loadingId = crypto.randomUUID();
    updateMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
      { id: loadingId, role: "assistant", status: "loading", progress: STATUS_LABELS.IN_QUEUE },
    ]);

    try {
      const result = await generateImage(trimmed, settings, (progress) => {
        updateMessages((prev) =>
          prev.map((message) =>
            message.id === loadingId ? { ...message, progress } : message
          )
        );
      });

      updateMessages((prev) => [
        ...prev.filter((message) => message.id !== loadingId),
        {
          id: crypto.randomUUID(),
          role: "assistant",
          status: "done",
          prompt: trimmed,
          imageBase64: result.image_base64,
          executionTimeMs: result.execution_time_ms,
          jobId: result.job_id,
        },
      ]);
    } catch (error) {
      updateMessages((prev) => [
        ...prev.filter((message) => message.id !== loadingId),
        {
          id: crypto.randomUUID(),
          role: "assistant",
          status: "error",
          content: error.message,
          retryPrompt: trimmed,
        },
      ]);
    } finally {
      setIsGenerating(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    runGeneration(prompt);
  }

  const configured = health?.endpoint_configured && health?.api_key_configured;

  return (
    <div className="app-shell">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onNewChat={startNewChat}
        onSelect={selectConversation}
        onDelete={deleteConversation}
        configured={configured}
        onOpenSettings={() => setSettingsOpen(true)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <main className="chat-panel">
        <header className="chat-header">
          <button className="mobile-menu" onClick={() => setMobileOpen(true)}>
            ☰
          </button>
          <div>
            <h2>{activeConversation?.title || "Flux Studio"}</h2>
            <p>Describe an image. FLUX.1-dev generates it on RunPod Serverless.</p>
          </div>
        </header>

        <section className="messages">
          {messages.length === 0 ? (
            <EmptyState onSelectPrompt={setPrompt} />
          ) : (
            messages.map((message) => (
              <ChatMessage key={message.id} message={message} onRetry={runGeneration} />
            ))
          )}
          <div ref={bottomRef} />
        </section>

        <Composer
          prompt={prompt}
          onPromptChange={setPrompt}
          onSubmit={handleSubmit}
          isGenerating={isGenerating}
          onOpenSettings={() => setSettingsOpen(true)}
        />
      </main>

      {settingsOpen ? (
        <SettingsPanel
          settings={settings}
          onChange={setSettings}
          onClose={() => setSettingsOpen(false)}
        />
      ) : null}
    </div>
  );
}
