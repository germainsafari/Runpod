import { useEffect, useRef, useState } from "react";
import ChatMessage from "./components/ChatMessage";
import Composer from "./components/Composer";
import EmptyState from "./components/EmptyState";
import LibraryView from "./components/LibraryView";
import SearchModal from "./components/SearchModal";
import SettingsPanel from "./components/SettingsPanel";
import Sidebar from "./components/Sidebar";
import { useAppState } from "./hooks/useAppState";
import { fetchHealth, fetchJobStatus, submitGeneration } from "./utils/api";

const STATUS_LABELS = {
  IN_QUEUE: "Queued on RunPod…",
  IN_PROGRESS: "Generating on GPU…",
  COMPLETED: "Finalizing image…",
};

async function generateImage(prompt, settings, onProgress) {
  const submitBody = await submitGeneration(prompt, settings);
  const jobId = submitBody.job_id;
  onProgress(STATUS_LABELS.IN_QUEUE);

  const deadline = Date.now() + 540_000;
  while (Date.now() < deadline) {
    const statusBody = await fetchJobStatus(jobId);
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
    projects,
    settings,
    activeConversation,
    activeId,
    activeView,
    setActiveView,
    libraryItems,
    pinnedConversations,
    recentConversations,
    expandedProjects,
    startNewChat,
    selectConversation,
    deleteConversation,
    renameConversation,
    togglePinConversation,
    moveConversationToProject,
    createNewProject,
    renameProject,
    deleteProject,
    toggleProjectExpanded,
    setSettings,
    updateMessages,
  } = useAppState();

  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [health, setHealth] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const bottomRef = useRef(null);

  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "error" }));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isGenerating, activeView]);

  useEffect(() => {
    function handleShortcut(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === "o") {
        event.preventDefault();
        startNewChat();
      }
    }
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, [startNewChat]);

  async function runGeneration(rawPrompt) {
    const trimmed = rawPrompt.trim();
    if (!trimmed || isGenerating) return;

    setPrompt("");
    setIsGenerating(true);
    setMobileOpen(false);
    setActiveView("chat");

    const loadingId = crypto.randomUUID();
    updateMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed, createdAt: Date.now() },
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
          createdAt: Date.now(),
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
          createdAt: Date.now(),
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
  const activeProject = projects.find((project) => project.id === activeConversation?.projectId);

  return (
    <div className="app-shell">
      <Sidebar
        conversations={conversations}
        projects={projects}
        pinnedConversations={pinnedConversations}
        recentConversations={recentConversations}
        expandedProjects={expandedProjects}
        activeId={activeId}
        activeView={activeView}
        libraryCount={libraryItems.length}
        configured={configured}
        mobileOpen={mobileOpen}
        onNewChat={startNewChat}
        onSelect={(id) => {
          selectConversation(id);
          setMobileOpen(false);
        }}
        onDelete={deleteConversation}
        onRename={renameConversation}
        onTogglePin={togglePinConversation}
        onMoveToProject={moveConversationToProject}
        onCreateProject={createNewProject}
        onRenameProject={renameProject}
        onDeleteProject={deleteProject}
        onToggleProjectExpanded={toggleProjectExpanded}
        onOpenSettings={() => setSettingsOpen(true)}
        onOpenSearch={() => setSearchOpen(true)}
        onOpenLibrary={() => {
          setActiveView("library");
          setMobileOpen(false);
        }}
        onSetView={setActiveView}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <main className="chat-panel">
        <header className="chat-header">
          <button type="button" className="mobile-menu" onClick={() => setMobileOpen(true)}>
            ☰
          </button>
          <div className="chat-header-copy">
            <div className="chat-title-row">
              <h2>
                {activeView === "library"
                  ? "Library"
                  : activeConversation?.title || "Flux Studio"}
              </h2>
              {activeProject && activeView === "chat" ? (
                <span className="project-chip">{activeProject.name}</span>
              ) : null}
            </div>
            <p>
              {activeView === "library"
                ? "Browse and download every image you have created."
                : "Describe an image. FLUX.1-dev generates it on RunPod Serverless."}
            </p>
          </div>
          <div className="model-badge">FLUX.1-dev</div>
        </header>

        {activeView === "library" ? (
          <LibraryView
            items={libraryItems}
            onOpenChat={(conversationId) => {
              selectConversation(conversationId);
              setActiveView("chat");
            }}
          />
        ) : (
          <>
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
          </>
        )}
      </main>

      {settingsOpen ? (
        <SettingsPanel
          settings={settings}
          onChange={setSettings}
          onClose={() => setSettingsOpen(false)}
        />
      ) : null}

      {searchOpen ? (
        <SearchModal
          conversations={conversations}
          onSelect={selectConversation}
          onClose={() => setSearchOpen(false)}
        />
      ) : null}
    </div>
  );
}
