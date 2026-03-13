import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiFetch } from "../utils/api";
import Logo from "../components/Logo";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ fullName: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    const { fullName, email, password, confirm } = form;
    if (!fullName.trim() || !email.trim() || !password.trim()) { setError("Please fill in all fields."); return; }
    if (password !== confirm) { setError("Passwords do not match."); return; }
    if (password.length < 6) { setError("Password must be at least 6 characters."); return; }

    setLoading(true);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: { full_name: fullName.trim(), email: email.trim(), password },
      });
      navigate("/", { state: { registered: true } });
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card fade-up" style={{ maxWidth: 460 }}>
        <div className="auth-logo-wrap"><Logo /></div>
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join the B2B supplier platform</p>

        {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>⚠ {error}</div>}

        <form onSubmit={submit}>
          <div className="auth-field">
            <label>Full name</label>
            <input className="input" placeholder="John Marston" value={form.fullName} onChange={set("fullName")} />
          </div>
          <div className="auth-field">
            <label>Email address</label>
            <input className="input" type="email" placeholder="you@company.com" value={form.email} onChange={set("email")} />
          </div>
          <div className="form-grid-2" style={{ gap: 12, marginBottom: 0 }}>
            <div className="auth-field" style={{ marginBottom: 0 }}>
              <label>Password</label>
              <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={set("password")} />
            </div>
            <div className="auth-field" style={{ marginBottom: 0 }}>
              <label>Confirm</label>
              <input className="input" type="password" placeholder="••••••••" value={form.confirm} onChange={set("confirm")} />
            </div>
          </div>

          <div className="auth-actions">
            <button type="submit" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", padding: "12px" }} disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </div>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/">Sign in</Link>
        </p>
      </div>
    </div>
  );
}