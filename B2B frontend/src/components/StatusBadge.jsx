import React from "react";

const STATUS_MAP = {
  pending:   { cls: "badge-amber", label: "Pending" },
  confirmed: { cls: "badge-green", label: "Confirmed" },
  rejected:  { cls: "badge-red",   label: "Rejected" },
  accepted:  { cls: "badge-green", label: "Accepted" },
  active:    { cls: "badge-blue",  label: "Active" },
  inactive:  { cls: "badge-gray",  label: "Inactive" },
};

export default function StatusBadge({ status, label }) {
  const map = STATUS_MAP[status?.toLowerCase()] || { cls: "badge-gray", label: status };
  return <span className={`badge ${map.cls}`}>{label || map.label}</span>;
}
