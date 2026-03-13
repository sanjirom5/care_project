import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiFetch, formatTime } from "../utils/api";

export default function Chat() {
  const { token } = useAuth();
  const location = useLocation();
  const focusCustomer = location.state?.customerName || null;

  const [conversations, setConversations] = useState([]);
  const [messagesByConv, setMessagesByConv] = useState({});
  const [activeId, setActiveId] = useState(null);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Load conversations
  useEffect(() => {
    apiFetch("/conversations", { token })
      .then(data => {
        const list = Array.isArray(data) ? data : [];
        setConversations(list);
        if (list.length > 0 && !activeId) setActiveId(list[0].id);
      })
      .catch(() => {});
  }, [token]);

  // Load messages for active conv
  useEffect(() => {
    if (!activeId) return;
    apiFetch(`/conversations/${activeId}/messages`, { token })
      .then(data => setMessagesByConv(prev => ({ ...prev, [activeId]: Array.isArray(data) ? data : [] })))
      .catch(() => {});
  }, [activeId, token]);

  // Focus on customer from navigation state
  useEffect(() => {
    if (!focusCustomer || conversations.length === 0) return;
    const match = conversations.find(c => c.name === focusCustomer);
    if (match) setActiveId(match.id);
  }, [focusCustomer, conversations]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeId, messagesByConv[activeId]?.length]);

  const send = async () => {
    if (!text.trim() || !activeId || sending) return;
    const nowIso = new Date().toISOString();
    const newMsg = { id: Date.now(), sender: "supplier", content: text.trim(), timestamp: nowIso };

    // Optimistic update
    setMessagesByConv(prev => ({ ...prev, [activeId]: [...(prev[activeId] || []), newMsg] }));
    setConversations(prev => prev.map(c => c.id === activeId ? { ...c, lastMessage: newMsg.content, lastTime: nowIso } : c));
    setText("");
    setSending(true);

    try {
      await apiFetch(`/conversations/${activeId}/messages`, {
        token, method: "POST", body: { content: newMsg.content }
      });
    } catch {}
    setSending(false);
  };

  const handleKey = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  const sortedConvs = [...conversations].sort((a, b) =>
    new Date(b.lastTime || 0) - new Date(a.lastTime || 0)
  );

  const activeMessages = messagesByConv[activeId] || [];
  const activeConv = conversations.find(c => c.id === activeId) || null;

  return (
    <div className="fade-up">
      <div className="page-header">
        <div className="page-breadcrumb">Messaging</div>
        <h1 className="page-title">Chat</h1>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="chat-layout">
          {/* Sidebar */}
          <div className="chat-sidebar">
            <div className="chat-sidebar-title">Conversations</div>
            <div className="chat-convo-list">
              {sortedConvs.length === 0 && (
                <div className="empty-state" style={{ padding: "24px 12px" }}>
                  <div className="empty-icon" style={{ fontSize: 24 }}>💬</div>
                  <p>No conversations yet.</p>
                </div>
              )}
              {sortedConvs.map(conv => {
                const msgs = messagesByConv[conv.id] || [];
                const last = msgs[msgs.length - 1];
                return (
                  <div
                    key={conv.id}
                    className={`chat-convo-item ${conv.id === activeId ? "active" : ""}`}
                    onClick={() => setActiveId(conv.id)}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 3 }}>
                      <div className="chat-convo-name">{conv.name}</div>
                      {(last?.timestamp || conv.lastTime) && (
                        <span className="meta">{formatTime(last?.timestamp || conv.lastTime)}</span>
                      )}
                    </div>
                    <div className="chat-convo-preview">
                      {last?.content || conv.lastMessage || "No messages yet"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Main chat */}
          <div className="chat-main">
            <div className="chat-header">
              {activeConv ? (
                <>
                  <div style={{ width: 34, height: 34, borderRadius: "50%", background: "var(--accent-soft)", display: "grid", placeItems: "center", fontWeight: 700, fontSize: 13, color: "var(--accent)", flexShrink: 0 }}>
                    {activeConv.name?.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{activeConv.name}</div>
                    <div className="meta">Customer</div>
                  </div>
                </>
              ) : (
                <span className="muted" style={{ fontSize: 14 }}>Select a conversation to start chatting</span>
              )}
            </div>

            <div className="chat-messages">
              {activeMessages.length === 0 && activeConv && (
                <div className="empty-state">
                  <div className="empty-icon">💬</div>
                  <p>No messages yet. Start the conversation!</p>
                </div>
              )}
              {activeMessages.map(m => (
                <div key={m.id} style={{ display: "flex", flexDirection: "column", alignItems: m.sender === "supplier" ? "flex-end" : "flex-start" }}>
                  <div className={`chat-bubble ${m.sender === "supplier" ? "mine" : "theirs"}`}>
                    {m.content}
                    <div className="chat-time">{formatTime(m.timestamp)}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-row">
              <input
                className="input"
                style={{ flex: 1 }}
                placeholder={activeConv ? "Type a message…" : "Select a conversation first"}
                value={text}
                onChange={e => setText(e.target.value)}
                onKeyDown={handleKey}
                disabled={!activeConv}
              />
              <button className="btn btn-primary btn-sm" onClick={send} disabled={!activeConv || sending}>
                {sending ? "…" : "Send"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
