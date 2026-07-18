import { useEffect, useState } from "react";
import {
  createConversation,
  deriveTitle,
  loadConversations,
  saveConversations,
} from "../utils/storage";

export function useConversations() {
  const [conversations, setConversations] = useState(() => loadConversations());
  const [activeId, setActiveId] = useState(() => {
    const saved = loadConversations();
    return saved[0]?.id ?? null;
  });

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  const activeConversation =
    conversations.find((conversation) => conversation.id === activeId) ??
    conversations[0] ??
    null;

  function ensureActiveConversation() {
    if (activeConversation) return activeConversation;

    const conversation = createConversation();
    setConversations((prev) => [conversation, ...prev]);
    setActiveId(conversation.id);
    return conversation;
  }

  function startNewChat() {
    const conversation = createConversation();
    setConversations((prev) => [conversation, ...prev]);
    setActiveId(conversation.id);
  }

  function selectConversation(id) {
    setActiveId(id);
  }

  function deleteConversation(id) {
    setConversations((prev) => {
      const next = prev.filter((conversation) => conversation.id !== id);
      if (activeId === id) {
        setActiveId(next[0]?.id ?? null);
      }
      return next;
    });
  }

  function updateMessages(updater) {
    setConversations((prev) => {
      const targetId = activeId ?? prev[0]?.id;
      if (!targetId) {
        const created = createConversation();
        setActiveId(created.id);
        const messages = typeof updater === "function" ? updater([]) : updater;
        return [{ ...created, messages, title: deriveTitle(messages), updatedAt: Date.now() }];
      }

      return prev.map((conversation) => {
        if (conversation.id !== targetId) return conversation;
        const messages =
          typeof updater === "function" ? updater(conversation.messages) : updater;
        return {
          ...conversation,
          messages,
          title: deriveTitle(messages),
          updatedAt: Date.now(),
        };
      });
    });
  }

  return {
    conversations,
    activeConversation: activeConversation ?? ensureActiveConversation(),
    activeId,
    startNewChat,
    selectConversation,
    deleteConversation,
    updateMessages,
  };
}
