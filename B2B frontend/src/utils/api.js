export const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiFetch(path, { token, method = "GET", body, formEncoded } = {}) {
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let bodyPayload;
  if (formEncoded) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    bodyPayload = new URLSearchParams(body);
  } else if (body) {
    headers["Content-Type"] = "application/json";
    bodyPayload = JSON.stringify(body);
  }

  const res = await fetch(BASE + path, { method, headers, body: bodyPayload });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const formatKZT = (value) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "KZT",
    maximumFractionDigits: 0,
  }).format(value);

export const formatDateTime = (ts) =>
  new Date(ts).toLocaleString([], {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });

export const formatTime = (ts) =>
  new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
