const STORAGE_KEY = "flux-chat-conversations";

export function loadConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveConversations(conversations) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

export function createConversation(title = "New chat") {
  return {
    id: crypto.randomUUID(),
    title,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [],
  };
}

export function deriveTitle(messages) {
  const firstUser = messages.find((message) => message.role === "user");
  if (!firstUser?.content) return "New chat";
  return firstUser.content.length > 42
    ? `${firstUser.content.slice(0, 42)}…`
    : firstUser.content;
}
