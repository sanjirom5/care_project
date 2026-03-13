import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../utils/api";
import Logo from "../components/Logo";

export default function LoginPage() {
  const { setToken } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const doLogin = async (e) => {
    e?.preventDefault();
    setError("");
    if (!email.trim() || !password.trim()) { setError("Please fill in all fields."); return; }
    if (email === "supplier@example.com" && password === "password") {
      setToken("demo-token");
      navigate("/dashboard");
      return;
    }
    setLoading(true);
    try {
      const data = await apiFetch("/auth/token", {
        method: "POST",
        formEncoded: true,
        body: { username: email, password },
      });
      if (data.access_token) {
        setToken(data.access_token);
        navigate("/dashboard");
      } else {
        setError("Invalid credentials. Please try again.");
      }
    } catch (err) {
      setError(err.message || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card fade-up">
        <div className="auth-logo-wrap"><Logo /></div>
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your supplier account</p>

        {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>⚠ {error}</div>}

        <form onSubmit={doLogin}>
          <div className="auth-field">
            <label>Email address</label>
            <input
              className="input"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <div className="auth-actions">
            <button type="submit" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", padding: "12px" }} disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </div>
        </form>

        <div className="auth-divider">or</div>
        <button
          className="btn btn-secondary"
          style={{ width: "100%", justifyContent: "center" }}
          onClick={() => { setEmail("supplier@example.com"); setPassword("password"); }}
        >
          Use demo credentials
        </button>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}
