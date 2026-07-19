import { useState } from "react";
import {
  ChatIcon,
  ChevronIcon,
  EditIcon,
  FolderIcon,
  LibraryIcon,
  MoreIcon,
  PinIcon,
  PlusIcon,
  SearchIcon,
  SparkIcon,
  TrashIcon,
} from "./Icons";
import ContextMenu from "./ContextMenu";
import { formatRelativeTime } from "../utils/storage";

function ConversationRow({
  conversation,
  active,
  onSelect,
  onContextMenu,
}) {
  return (
    <div className={`conversation-item ${active ? "active" : ""}`}>
      <button type="button" className="conversation-button" onClick={() => onSelect(conversation.id)}>
        <span className="conversation-title">{conversation.title}</span>
        <span className="conversation-time">{formatRelativeTime(conversation.updatedAt)}</span>
      </button>
      <button
        type="button"
        className="icon-button subtle conversation-menu"
        aria-label="Chat options"
        onClick={(event) => onContextMenu(event, conversation)}
      >
        <MoreIcon />
      </button>
    </div>
  );
}

export default function Sidebar({
  conversations,
  projects,
  pinnedConversations,
  recentConversations,
  expandedProjects,
  activeId,
  activeView,
  libraryCount,
  configured,
  mobileOpen,
  onNewChat,
  onSelect,
  onDelete,
  onRename,
  onTogglePin,
  onMoveToProject,
  onCreateProject,
  onRenameProject,
  onDeleteProject,
  onToggleProjectExpanded,
  onOpenSettings,
  onOpenSearch,
  onOpenLibrary,
  onSetView,
  onCloseMobile,
}) {
  const [contextMenu, setContextMenu] = useState(null);
  const [newProjectOpen, setNewProjectOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");

  function openConversationMenu(event, conversation) {
    event.preventDefault();
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    setContextMenu({
      x: Math.min(rect.right, window.innerWidth - 220),
      y: rect.bottom + 4,
      items: [
        {
          key: "pin",
          label: conversation.pinned ? "Unpin chat" : "Pin chat",
          icon: <PinIcon filled={conversation.pinned} />,
          onClick: () => onTogglePin(conversation.id),
        },
        {
          key: "rename",
          label: "Rename",
          icon: <EditIcon />,
          onClick: () => {
            const next = window.prompt("Rename chat", conversation.title);
            if (next) onRename(conversation.id, next);
          },
        },
        { key: "sep1", separator: true },
        ...projects.map((project) => ({
          key: `project-${project.id}`,
          label: `Move to ${project.name}`,
          icon: <FolderIcon />,
          onClick: () => onMoveToProject(conversation.id, project.id),
        })),
        {
          key: "remove-project",
          label: "Remove from project",
          onClick: () => onMoveToProject(conversation.id, null),
        },
        { key: "sep2", separator: true },
        {
          key: "delete",
          label: "Delete chat",
          icon: <TrashIcon />,
          danger: true,
          onClick: () => {
            if (window.confirm("Delete this chat permanently?")) {
              onDelete(conversation.id);
            }
          },
        },
      ],
    });
  }

  function handleCreateProject(event) {
    event.preventDefault();
    if (!newProjectName.trim()) return;
    onCreateProject(newProjectName);
    setNewProjectName("");
    setNewProjectOpen(false);
  }

  const ungroupedRecent = recentConversations.filter((conversation) => !conversation.projectId);

  return (
    <>
      {mobileOpen ? (
        <button type="button" className="sidebar-overlay" onClick={onCloseMobile} aria-label="Close menu" />
      ) : null}

      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-mark">
              <SparkIcon />
            </div>
            <div>
              <h1>Flux Studio</h1>
              <p>FLUX.1-dev · RunPod</p>
            </div>
          </div>

          <button type="button" className="primary-button new-chat" onClick={() => onNewChat()}>
            <PlusIcon />
            New chat
          </button>

          <button type="button" className="sidebar-nav-button" onClick={onOpenSearch}>
            <SearchIcon />
            Search chats
            <kbd>Ctrl K</kbd>
          </button>
        </div>

        <div className="sidebar-nav">
          <button
            type="button"
            className={`sidebar-nav-button ${activeView === "chat" ? "active" : ""}`}
            onClick={() => onSetView("chat")}
          >
            <ChatIcon />
            Chats
          </button>
          <button
            type="button"
            className={`sidebar-nav-button ${activeView === "library" ? "active" : ""}`}
            onClick={onOpenLibrary}
          >
            <LibraryIcon />
            Library
            {libraryCount ? <span className="nav-count">{libraryCount}</span> : null}
          </button>
        </div>

        <div className="conversation-list">
          {pinnedConversations.length ? (
            <section className="sidebar-section">
              <p className="section-label">
                <PinIcon filled />
                Pinned
              </p>
              {pinnedConversations.map((conversation) => (
                <ConversationRow
                  key={conversation.id}
                  conversation={conversation}
                  active={conversation.id === activeId && activeView === "chat"}
                  onSelect={onSelect}
                  onContextMenu={openConversationMenu}
                />
              ))}
            </section>
          ) : null}

          <section className="sidebar-section">
            <div className="section-header">
              <p className="section-label">
                <FolderIcon />
                Projects
              </p>
              <button
                type="button"
                className="icon-button subtle"
                aria-label="New project"
                onClick={() => setNewProjectOpen((value) => !value)}
              >
                <PlusIcon />
              </button>
            </div>

            {newProjectOpen ? (
              <form className="inline-form" onSubmit={handleCreateProject}>
                <input
                  value={newProjectName}
                  onChange={(event) => setNewProjectName(event.target.value)}
                  placeholder="Project name"
                  autoFocus
                />
                <button type="submit" className="ghost-button compact">
                  Add
                </button>
              </form>
            ) : null}

            {projects.length === 0 ? (
              <p className="empty-list">Organize chats into projects</p>
            ) : (
              projects.map((project) => {
                const projectChats = conversations
                  .filter((conversation) => conversation.projectId === project.id)
                  .sort((a, b) => b.updatedAt - a.updatedAt);
                const open = expandedProjects[project.id] ?? true;

                return (
                  <div key={project.id} className="project-group">
                    <div className="project-header">
                      <button
                        type="button"
                        className="project-toggle"
                        onClick={() => onToggleProjectExpanded(project.id)}
                      >
                        <ChevronIcon open={open} />
                        <span>{project.name}</span>
                        <span className="project-count">{projectChats.length}</span>
                      </button>
                      <button
                        type="button"
                        className="icon-button subtle"
                        aria-label="Project options"
                        onClick={() => {
                          const action = window.prompt(
                            `Project "${project.name}"\nType rename:NEW NAME or delete`,
                            "rename:"
                          );
                          if (!action) return;
                          if (action.startsWith("rename:")) {
                            onRenameProject(project.id, action.slice(7));
                          } else if (action === "delete" && window.confirm("Delete this project? Chats will be kept.")) {
                            onDeleteProject(project.id);
                          }
                        }}
                      >
                        <MoreIcon />
                      </button>
                    </div>
                    {open ? (
                      <div className="project-chats">
                        <button
                          type="button"
                          className="ghost-button compact project-new-chat"
                          onClick={() => onNewChat(project.id)}
                        >
                          <PlusIcon />
                          New chat in project
                        </button>
                        {projectChats.length === 0 ? (
                          <p className="empty-list nested">No chats yet</p>
                        ) : (
                          projectChats.map((conversation) => (
                            <ConversationRow
                              key={conversation.id}
                              conversation={conversation}
                              active={conversation.id === activeId && activeView === "chat"}
                              onSelect={onSelect}
                              onContextMenu={openConversationMenu}
                            />
                          ))
                        )}
                      </div>
                    ) : null}
                  </div>
                );
              })
            )}
          </section>

          <section className="sidebar-section">
            <p className="section-label">Recent</p>
            {ungroupedRecent.length === 0 ? (
              <p className="empty-list">No recent chats</p>
            ) : (
              ungroupedRecent.map((conversation) => (
                <ConversationRow
                  key={conversation.id}
                  conversation={conversation}
                  active={conversation.id === activeId && activeView === "chat"}
                  onSelect={onSelect}
                  onContextMenu={openConversationMenu}
                />
              ))
            )}
          </section>
        </div>

        <div className="sidebar-footer">
          <button type="button" className="ghost-button footer-button" onClick={onOpenSettings}>
            <SparkIcon />
            Settings & model
          </button>
          <div className={`status-pill ${configured ? "ok" : "warn"}`}>
            <span className="status-dot" />
            {configured ? "RunPod connected" : "Configure API keys"}
          </div>
        </div>
      </aside>

      {contextMenu ? (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          items={contextMenu.items}
          onClose={() => setContextMenu(null)}
        />
      ) : null}
    </>
  );
}
