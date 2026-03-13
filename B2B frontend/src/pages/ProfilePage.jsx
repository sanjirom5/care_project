import React, { useState } from "react";

export default function ProfilePage() {
  const [about, setAbout] = useState(() => {
    try { return localStorage.getItem("supplierAbout") || ""; } catch { return ""; }
  });
  const [visible, setVisible] = useState(() => {
    try { return localStorage.getItem("supplierVisible") === "true"; } catch { return false; }
  });
  const [editing, setEditing] = useState(false);
  const [tempAbout, setTempAbout] = useState(about);

  const saveAbout = () => {
    setAbout(tempAbout);
    try { localStorage.setItem("supplierAbout", tempAbout); } catch {}
    setEditing(false);
  };

  const toggleVisible = () => {
    const next = !visible;
    setVisible(next);
    try { localStorage.setItem("supplierVisible", String(next)); } catch {}
  };

  return (
    <div className="fade-up" style={{ maxWidth: 640 }}>
      <div className="page-header">
        <div className="page-breadcrumb">Account</div>
        <h1 className="page-title">Supplier Profile</h1>
      </div>

      {/* Visibility toggle */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div className="section-title" style={{ marginBottom: 4 }}>Visibility</div>
            <p className="muted" style={{ fontSize: 13 }}>
              {visible ? "Your store is visible to customers on the platform." : "Your store is hidden from customers."}
            </p>
          </div>
          <button
            className="btn"
            style={{
              background: visible ? "var(--green-soft)" : "var(--red-soft)",
              color: visible ? "var(--green)" : "var(--red)",
              border: `1px solid ${visible ? "rgba(13,148,136,.2)" : "rgba(220,38,38,.15)"}`,
              minWidth: 130,
              justifyContent: "center",
            }}
            onClick={toggleVisible}
          >
            {visible ? "● Visible" : "○ Hidden"}
          </button>
        </div>
      </div>

      {/* About */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div className="section-title" style={{ marginBottom: 0 }}>About your business</div>
          {!editing && (
            <button className="btn btn-ghost btn-sm" onClick={() => { setTempAbout(about); setEditing(true); }}>
              Edit
            </button>
          )}
        </div>

        {editing ? (
          <>
            <textarea
              className="input"
              style={{ minHeight: 140, marginBottom: 14 }}
              placeholder="Describe your business, products you specialize in, delivery regions, etc."
              value={tempAbout}
              onChange={e => setTempAbout(e.target.value)}
              autoFocus
            />
            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn-primary btn-sm" onClick={saveAbout}>Save changes</button>
              <button className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </>
        ) : (
          about.trim()
            ? <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-2)", whiteSpace: "pre-wrap" }}>{about}</p>
            : <div className="empty-state" style={{ padding: "20px 0" }}>
                <div className="empty-icon">✏️</div>
                <p>No description yet. Click Edit to add information about your business.</p>
              </div>
        )}
      </div>
    </div>
  );
}
