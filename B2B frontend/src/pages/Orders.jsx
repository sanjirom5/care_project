import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/api";

export default function Orders() {
  const navigate = useNavigate();
  const [orders] = useState([]);
  const [filter, setFilter] = useState("all");

  const STATUS_TABS = [
    { value: "all", label: "All" },
    { value: "pending", label: "Pending" },
    { value: "confirmed", label: "Confirmed" },
    { value: "rejected", label: "Rejected" },
  ];

  const displayed = filter === "all" ? orders : orders.filter(o => o.status === filter);

  return (
    <div className="fade-up">
      <div className="page-header">
        <div className="page-breadcrumb">Orders</div>
        <div className="page-header-row">
          <h1 className="page-title">Orders</h1>
          <span className="badge badge-blue">{orders.length} total</span>
        </div>
      </div>

      {/* Filter tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 20 }}>
        {STATUS_TABS.map(t => (
          <button
            key={t.value}
            onClick={() => setFilter(t.value)}
            className={`btn btn-sm ${filter === t.value ? "btn-primary" : "btn-ghost"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="card">
        {displayed.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>{orders.length === 0 ? "No orders yet. They'll appear here once customers place them." : "No orders match this filter."}</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Delivery</th>
                <th>Amount</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {displayed.map(o => (
                <tr
                  key={o.id}
                  style={{ cursor: "pointer" }}
                  onClick={() => navigate(`/orders/${o.id}`)}
                >
                  <td>
                    <span className="strong" style={{ fontFamily: "var(--font-mono)", fontSize: 13 }}>#{o.id}</span>
                  </td>
                  <td>{o.consumer_name}</td>
                  <td><span className="meta">{formatDateTime(o.created_at)}</span></td>
                  <td>
                    <span className="badge badge-gray">
                      {o.delivery_type === "delivery" ? "🚚 Delivery" : "🏪 Pickup"}
                    </span>
                  </td>
                  <td><span className="strong">{o.total_amount} ₸</span></td>
                  <td><StatusBadge status={o.status} /></td>
                  <td style={{ textAlign: "right" }}>
                    <button className="btn btn-ghost btn-xs" onClick={e => { e.stopPropagation(); navigate(`/orders/${o.id}`); }}>
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
