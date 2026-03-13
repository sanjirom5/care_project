import React from "react";

export default function Logo({ small }) {
  const size = small ? 32 : 40;
  const fontSize = small ? 15 : 18;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div
        style={{
          width: size, height: size,
          borderRadius: small ? 8 : 10,
          background: "linear-gradient(135deg, #3b5bdb 0%, #5b78e5 100%)",
          display: "grid", placeItems: "center",
          boxShadow: "0 4px 12px rgba(59,91,219,0.25)",
          flexShrink: 0,
        }}
      >
        <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 22 22" fill="none">
          <rect x="2" y="2" width="8" height="8" rx="2" fill="white" opacity=".9"/>
          <rect x="12" y="2" width="8" height="8" rx="2" fill="white" opacity=".6"/>
          <rect x="2" y="12" width="8" height="8" rx="2" fill="white" opacity=".6"/>
          <rect x="12" y="12" width="8" height="8" rx="2" fill="white" opacity=".9"/>
        </svg>
      </div>
      <span style={{
        fontWeight: 800,
        fontSize,
        color: "var(--text)",
        letterSpacing: "-0.4px",
        lineHeight: 1,
      }}>
        B2B<span style={{ color: "var(--accent)", fontWeight: 700 }}>Hub</span>
      </span>
    </div>
  );
}
