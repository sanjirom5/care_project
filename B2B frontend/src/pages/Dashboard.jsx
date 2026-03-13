import React, { useState } from "react";
import { Link } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/api";

export default function Dashboard() {
  const [linkRequests, setLinkRequests] = useState([]);

  const updateLink = (id, status) =>
    setLinkRequests(prev => prev.map(l => l.id === id ? { ...l, status } : l));

  const pendingLinks = linkRequests.filter(l => l.status === "pending").length;

  const STATS = [
    { label: "Orders today",    value: 0, sub: "New today",               icon: "📦", color: "#3b5bdb" },
    { label: "Pending orders",  value: 0, sub: "Awaiting confirmation",   icon: "⏳", color: "#d97706" },
    { label: "Active chats",    value: 0, sub: "Ongoing conversations",   icon: "💬", color: "#0d9488" },
    { label: "Link requests",   value: pendingLinks, sub: "Pending connections", icon: "🔗", color: "#7c3aed" },
  ];

  return (
    <div className="fade-up">
      <div className="page-header">
        <div className="page-breadcrumb">Overview</div>
        <div className="page-header-row">
          <h1 className="page-title">Supplier Dashboard</h1>
        </div>
        <p className="muted" style={{ marginTop: 4 }}>
          Welcome back. Here's what's happening with your store.
        </p>
      </div>

      {/* Stats grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}
           className="stagger">
        {STATS.map(s => (
          <div key={s.label} className="stat-card fade-up" style={{ "--accent-bar": s.color }}>
            <div className="stat-icon" style={{ background: s.color + "15" }}>
              <span>{s.icon}</span>
            </div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Two panels */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 20 }}>
        {/* Link requests */}
        <div className="card">
          <div className="section-title">Incoming Link Requests</div>
          <p className="muted" style={{ marginBottom: 16, fontSize: 13 }}>
            Approve or reject connection requests from customers.
          </p>
          {linkRequests.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔗</div>
              <p>No link requests yet. They'll appear here when customers want to connect.</p>
            </div>
          ) : (
            <div>
              {linkRequests.map(lr => (
                <div key={lr.id} className="list-row" style={{ flexDirection: "column", alignItems: "stretch", gap: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div className="strong" style={{ fontSize: 14 }}>{lr.consumerName}</div>
                      <div className="meta">{formatDateTime(lr.createdAt)}</div>
                    </div>
                    <StatusBadge status={lr.status} />
                  </div>
                  {lr.status === "pending" && (
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="btn btn-primary btn-sm" onClick={() => updateLink(lr.id, "accepted")}>Approve</button>
                      <button className="btn btn-ghost btn-sm" onClick={() => updateLink(lr.id, "rejected")}>Decline</button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent orders */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div className="section-title" style={{ marginBottom: 0 }}>Recent Orders</div>
            <Link to="/orders" style={{ fontSize: 12, color: "var(--accent)", fontWeight: 600 }}>View all →</Link>
          </div>
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No orders yet. They will appear here once customers place them.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
