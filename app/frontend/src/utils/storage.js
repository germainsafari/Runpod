const CONVERSATIONS_KEY = "flux-chat-conversations";
const PROJECTS_KEY = "flux-chat-projects";
const SETTINGS_KEY = "flux-chat-settings";

export const DEFAULT_SETTINGS = {
  num_inference_steps: 20,
  guidance_scale: 3.5,
  width: 512,
  height: 512,
  seed: null,
};

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function loadConversations() {
  const conversations = readJson(CONVERSATIONS_KEY, []);
  return conversations.map((conversation) => ({
    pinned: false,
    projectId: null,
    ...conversation,
  }));
}

export function saveConversations(conversations) {
  writeJson(CONVERSATIONS_KEY, conversations);
}

export function loadProjects() {
  return readJson(PROJECTS_KEY, []);
}

export function saveProjects(projects) {
  writeJson(PROJECTS_KEY, projects);
}

export function loadSettings() {
  return { ...DEFAULT_SETTINGS, ...readJson(SETTINGS_KEY, {}) };
}

export function saveSettings(settings) {
  writeJson(SETTINGS_KEY, settings);
}

export function createConversation(title = "New chat", projectId = null) {
  return {
    id: crypto.randomUUID(),
    title,
    projectId,
    pinned: false,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [],
  };
}

export function createProject(name = "Untitled project") {
  return {
    id: crypto.randomUUID(),
    name,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
}

export function deriveTitle(messages) {
  const firstUser = messages.find((message) => message.role === "user");
  if (!firstUser?.content) return "New chat";
  return firstUser.content.length > 42
    ? `${firstUser.content.slice(0, 42)}…`
    : firstUser.content;
}

export function collectLibraryItems(conversations) {
  const items = [];

  for (const conversation of conversations) {
    for (const message of conversation.messages) {
      if (message.role === "assistant" && message.status === "done" && message.imageBase64) {
        items.push({
          id: message.id,
          conversationId: conversation.id,
          conversationTitle: conversation.title,
          prompt: message.prompt || "Generated image",
          imageBase64: message.imageBase64,
          executionTimeMs: message.executionTimeMs,
          jobId: message.jobId,
          createdAt: message.createdAt || conversation.updatedAt,
        });
      }
    }
  }

  return items.sort((a, b) => b.createdAt - a.createdAt);
}

export function formatRelativeTime(timestamp) {
  const diff = Date.now() - timestamp;
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(timestamp).toLocaleDateString();
}
