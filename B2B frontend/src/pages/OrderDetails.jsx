import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/api";

export default function OrderDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null); // will be fetched from backend

  if (!order) {
    return (
      <div className="fade-up">
        <div className="page-header">
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/orders")}>← Back to Orders</button>
        </div>
        <div className="card" style={{ maxWidth: 680, margin: "0 auto" }}>
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <p>Order #{id} not found or hasn't loaded yet.</p>
            <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={() => navigate("/orders")}>
              Back to Orders
            </button>
          </div>
        </div>
      </div>
    );
  }

  const accept = () => setOrder(o => ({ ...o, status: "confirmed" }));
  const reject = () => {
    if (!confirm("Reject this order? This cannot be undone.")) return;
    setOrder(o => ({ ...o, status: "rejected" }));
  };
  const goChat = () => navigate("/chat", { state: { customerName: order.consumer_name } });

  return (
    <div className="fade-up">
      <div className="page-header">
        <button className="btn btn-ghost btn-sm" onClick={() => navigate("/orders")}>← Back to Orders</button>
        <div className="page-header-row" style={{ marginTop: 12 }}>
          <div>
            <h1 className="page-title">Order #{order.id}</h1>
            <p className="muted" style={{ marginTop: 4 }}>{formatDateTime(order.created_at)}</p>
          </div>
          <StatusBadge status={order.status} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, maxWidth: 860 }}>
        <div className="card">
          <div className="section-title">Order Info</div>
          <div style={{ display: "grid", gap: 14 }}>
            {[
              { label: "Customer",  value: order.consumer_name },
              { label: "Delivery",  value: order.delivery_type === "delivery" ? "🚚 Delivery" : "🏪 Pickup" },
              { label: "Total",     value: `${order.total_amount} ₸` },
              { label: "Status",    value: <StatusBadge status={order.status} /> },
            ].map(row => (
              <div key={row.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="label">{row.label}</span>
                <span style={{ fontWeight: 500, fontSize: 14 }}>{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="section-title">Order Items</div>
          <div className="empty-state" style={{ padding: "24px 0" }}>
            <div className="empty-icon">📦</div>
            <p>Items will load from <code style={{ fontSize: 11, background: "var(--surface-2)", padding: "2px 6px", borderRadius: 4 }}>/orders/{order.id}/items</code></p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div style={{ marginTop: 24, display: "flex", gap: 10 }}>
        <button className="btn btn-primary" onClick={goChat}>💬 Chat with {order.consumer_name}</button>
        {order.status === "pending" && (
          <>
            <button className="btn btn-secondary" onClick={accept}>✓ Accept Order</button>
            <button className="btn btn-danger" onClick={reject}>✕ Reject Order</button>
          </>
        )}
      </div>
    </div>
  );
}
