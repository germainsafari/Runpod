import { useEffect, useMemo, useState } from "react";
import {
  collectLibraryItems,
  createConversation,
  createProject,
  deriveTitle,
  loadConversations,
  loadProjects,
  loadSettings,
  saveConversations,
  saveProjects,
  saveSettings,
} from "../utils/storage";

export function useAppState() {
  const [conversations, setConversations] = useState(() => loadConversations());
  const [projects, setProjects] = useState(() => loadProjects());
  const [settings, setSettingsState] = useState(() => loadSettings());
  const [activeId, setActiveId] = useState(() => loadConversations()[0]?.id ?? null);
  const [activeView, setActiveView] = useState("chat");
  const [expandedProjects, setExpandedProjects] = useState(() =>
    Object.fromEntries(loadProjects().map((project) => [project.id, true]))
  );

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  useEffect(() => {
    saveProjects(projects);
  }, [projects]);

  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  const libraryItems = useMemo(() => collectLibraryItems(conversations), [conversations]);

  const activeConversation =
    conversations.find((conversation) => conversation.id === activeId) ??
    conversations[0] ??
    null;

  const pinnedConversations = useMemo(
    () =>
      conversations
        .filter((conversation) => conversation.pinned)
        .sort((a, b) => b.updatedAt - a.updatedAt),
    [conversations]
  );

  const recentConversations = useMemo(
    () =>
      conversations
        .filter((conversation) => !conversation.pinned)
        .sort((a, b) => b.updatedAt - a.updatedAt),
    [conversations]
  );

  function ensureActiveConversation() {
    if (activeConversation) return activeConversation;
    const conversation = createConversation();
    setConversations((prev) => [conversation, ...prev]);
    setActiveId(conversation.id);
    return conversation;
  }

  function startNewChat(projectId = null) {
    const conversation = createConversation("New chat", projectId);
    setConversations((prev) => [conversation, ...prev]);
    setActiveId(conversation.id);
    setActiveView("chat");
  }

  function selectConversation(id) {
    setActiveId(id);
    setActiveView("chat");
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

  function renameConversation(id, title) {
    const trimmed = title.trim();
    if (!trimmed) return;
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === id
          ? { ...conversation, title: trimmed, updatedAt: Date.now() }
          : conversation
      )
    );
  }

  function togglePinConversation(id) {
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === id
          ? { ...conversation, pinned: !conversation.pinned, updatedAt: Date.now() }
          : conversation
      )
    );
  }

  function moveConversationToProject(id, projectId) {
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === id
          ? { ...conversation, projectId, updatedAt: Date.now() }
          : conversation
      )
    );
  }

  function createNewProject(name) {
    const project = createProject(name.trim() || "Untitled project");
    setProjects((prev) => [project, ...prev]);
    setExpandedProjects((prev) => ({ ...prev, [project.id]: true }));
    return project;
  }

  function renameProject(id, name) {
    const trimmed = name.trim();
    if (!trimmed) return;
    setProjects((prev) =>
      prev.map((project) =>
        project.id === id ? { ...project, name: trimmed, updatedAt: Date.now() } : project
      )
    );
  }

  function deleteProject(id) {
    setProjects((prev) => prev.filter((project) => project.id !== id));
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.projectId === id ? { ...conversation, projectId: null } : conversation
      )
    );
  }

  function toggleProjectExpanded(id) {
    setExpandedProjects((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  function setSettings(next) {
    setSettingsState(next);
  }

  function searchConversations(query) {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return [];

    return conversations
      .map((conversation) => {
        const titleMatch = conversation.title.toLowerCase().includes(normalized);
        const messageMatch = conversation.messages.some((message) => {
          const text = message.content || message.prompt || "";
          return text.toLowerCase().includes(normalized);
        });
        if (!titleMatch && !messageMatch) return null;
        return conversation;
      })
      .filter(Boolean)
      .sort((a, b) => b.updatedAt - a.updatedAt);
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
        const stamped = messages.map((message) =>
          message.createdAt ? message : { ...message, createdAt: Date.now() }
        );
        return {
          ...conversation,
          messages: stamped,
          title: deriveTitle(stamped),
          updatedAt: Date.now(),
        };
      });
    });
  }

  return {
    conversations,
    projects,
    settings,
    activeConversation: activeConversation ?? ensureActiveConversation(),
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
    searchConversations,
    updateMessages,
  };
}
