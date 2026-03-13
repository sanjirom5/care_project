import React from "react";
import Logo from "../components/Logo";

const TEAM = [
  { name: "Aldiyar Kunduskairov", role: "Backend Engineer" },
  { name: "Rauan Kozhakhmetov",   role: "Mobile (Flutter)" },
  { name: "Sanzhar Umirbayev",    role: "Frontend Engineer" },
  { name: "Sayat Mushkin",        role: "Full Stack" },
];

export default function AboutPage() {
  return (
    <div className="fade-up" style={{ maxWidth: 640 }}>
      <div className="page-header">
        <h1 className="page-title">About</h1>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
          <Logo />
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>B2B Supplier Platform</div>
            <div className="muted" style={{ fontSize: 13 }}>Software Engineering Course Project</div>
          </div>
        </div>

        <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-2)", marginBottom: 14 }}>
          This platform allows suppliers to manage product catalogs, handle connection requests from consumers,
          process orders, and communicate with customers in real time.
        </p>
        <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-2)" }}>
          The system consists of three parts: this web frontend (React + Vite), a REST backend (FastAPI), and
          a mobile consumer app (Flutter).
        </p>
      </div>

      <div className="card">
        <div className="section-title">Team</div>
        <div style={{ display: "grid", gap: 10 }}>
          {TEAM.map((m, i) => (
            <div key={i} className="list-row">
              <div style={{ width: 36, height: 36, borderRadius: "50%", background: "var(--accent-soft)", display: "grid", placeItems: "center", fontWeight: 700, fontSize: 13, color: "var(--accent)", flexShrink: 0 }}>
                {m.name.charAt(0)}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{m.name}</div>
                <div className="meta">{m.role}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="divider" />
        <div className="muted" style={{ fontSize: 13 }}>
          Contact: <a href="https://t.me/snjroo" style={{ color: "var(--accent)", fontWeight: 600 }}>@snjroo</a> on Telegram
        </div>
      </div>
    </div>
  );
}
