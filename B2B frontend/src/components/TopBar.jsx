import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "./Logo";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "⊞" },
  { to: "/products",  label: "Products",  icon: "⬡" },
  { to: "/orders",    label: "Orders",    icon: "≡" },
  { to: "/chat",      label: "Chat",      icon: "◎" },
  { to: "/profile",   label: "Profile",   icon: "◑" },
];

export default function TopBar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <Logo small />
      </div>

      {token && (
        <nav className="topbar-nav">
          {NAV_ITEMS.map(({ to, label, icon }) => (
            <Link
              key={to}
              to={to}
              className={`topbar-nav-link ${pathname === to || pathname.startsWith(to + "/") ? "active" : ""}`}
            >
              <span style={{ fontSize: 13 }}>{icon}</span>
              {label}
            </Link>
          ))}
        </nav>
      )}

      <div className="topbar-actions">
        <Link
          to="/about"
          className={`topbar-nav-link ${pathname === "/about" ? "active" : ""}`}
          style={{ fontSize: 13 }}
        >
          About
        </Link>

        {!token ? (
          <>
            <Link to="/register" className="btn btn-ghost btn-sm">Register</Link>
            <button className="btn btn-primary btn-sm" onClick={() => navigate("/")}>Login</button>
          </>
        ) : (
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { logout(); navigate("/"); }}
          >
            Sign out
          </button>
        )}
      </div>
    </header>
  );
}
