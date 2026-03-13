import React, { useState } from "react";
import { formatKZT } from "../utils/api";

const EMPTY_FORM = { name: "", price: "", quantity: "", unit: "" };

export default function Products() {
  const [products, setProducts] = useState([]);
  const [filter, setFilter] = useState("");
  const [newProduct, setNewProduct] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [editFields, setEditFields] = useState(EMPTY_FORM);
  const [discountId, setDiscountId] = useState(null);
  const [discountInput, setDiscountInput] = useState("");
  const [addError, setAddError] = useState("");

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(filter.toLowerCase())
  );

  const setNew = key => e => setNewProduct(f => ({ ...f, [key]: e.target.value }));
  const setEdit = key => e => setEditFields(f => ({ ...f, [key]: e.target.value }));

  const handleAdd = (e) => {
    e.preventDefault();
    setAddError("");
    const { name, price, quantity, unit } = newProduct;
    if (!name.trim() || !price || !quantity || !unit.trim()) { setAddError("All fields are required."); return; }
    const p = parseFloat(price), q = parseInt(quantity, 10);
    if (isNaN(p) || p < 0) { setAddError("Price must be a positive number."); return; }
    if (isNaN(q) || q < 0) { setAddError("Quantity must be a positive number."); return; }
    setProducts(prev => [{ id: Date.now(), name: name.trim(), price: p, quantity: q, unit: unit.trim(), discountPercent: 0 }, ...prev]);
    setNewProduct(EMPTY_FORM);
  };

  const remove = id => { if (confirm("Remove this product?")) setProducts(p => p.filter(x => x.id !== id)); };

  const openEdit = id => {
    setDiscountId(null);
    const p = products.find(x => x.id === id);
    if (!p) return;
    setEditFields({ name: p.name, price: String(p.price), quantity: String(p.quantity), unit: p.unit });
    setEditingId(id);
  };

  const saveEdit = id => {
    const name = editFields.name.trim(), unit = editFields.unit.trim();
    const price = parseFloat(editFields.price), quantity = parseInt(editFields.quantity, 10);
    if (!name || !unit || isNaN(price) || isNaN(quantity)) { alert("Fill all fields correctly."); return; }
    setProducts(prev => prev.map(p => p.id === id ? { ...p, name, price, quantity: Math.max(0, quantity), unit } : p));
    setEditingId(null);
  };

  const openDiscount = id => {
    setEditingId(null);
    const p = products.find(x => x.id === id);
    setDiscountInput(p?.discountPercent ? String(p.discountPercent) : "");
    setDiscountId(id);
  };

  const applyDiscount = id => {
    const raw = discountInput.trim();
    const v = raw === "" ? 0 : Number(raw);
    if (isNaN(v) || v < 0 || v > 100) { alert("Enter a valid percent (0–100)."); return; }
    setProducts(prev => prev.map(p => p.id === id ? { ...p, discountPercent: Math.round(v) } : p));
    setDiscountId(null);
  };

  const handleRowKey = (e, action) => {
    if (e.key === "Enter") { e.preventDefault(); action(); }
    if (e.key === "Escape") { setEditingId(null); setDiscountId(null); }
  };

  return (
    <div className="fade-up">
      <div className="page-header">
        <div className="page-breadcrumb">Catalog</div>
        <div className="page-header-row">
          <h1 className="page-title">Product Catalog</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <input
              className="input"
              style={{ width: 220 }}
              placeholder="Search products…"
              value={filter}
              onChange={e => setFilter(e.target.value)}
            />
            <span className="muted" style={{ whiteSpace: "nowrap" }}>{products.length} items</span>
          </div>
        </div>
      </div>

      {/* Product list */}
      <div className="card" style={{ marginBottom: 20 }}>
        {filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <p>{products.length === 0 ? "No products yet. Add your first product below." : "No products match your search."}</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Stock</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(p => {
                const discounted = p.discountPercent > 0;
                const finalPrice = discounted ? Math.round(p.price * (1 - p.discountPercent / 100)) : p.price;
                return (
                  <React.Fragment key={p.id}>
                    <tr>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 14 }}>{p.name}</div>
                        <div className="meta">per {p.unit}</div>
                      </td>
                      <td>
                        {discounted ? (
                          <div>
                            <span style={{ textDecoration: "line-through", color: "var(--text-3)", fontSize: 12 }}>{formatKZT(p.price)}</span>
                            <span className="badge badge-green" style={{ marginLeft: 6 }}>-{p.discountPercent}%</span>
                            <div style={{ fontWeight: 700, fontSize: 14 }}>{formatKZT(finalPrice)}</div>
                          </div>
                        ) : (
                          <span style={{ fontWeight: 600, fontSize: 14 }}>{formatKZT(p.price)}</span>
                        )}
                      </td>
                      <td>
                        {p.quantity > 0
                          ? <span style={{ fontSize: 14 }}>{p.quantity} <span className="muted">in stock</span></span>
                          : <span className="badge badge-red">Out of stock</span>}
                      </td>
                      <td>
                        <div style={{ display: "flex", justifyContent: "flex-end", gap: 6 }}>
                          <button className="btn btn-ghost btn-xs" onClick={() => openDiscount(p.id)}>% Discount</button>
                          <button className="btn btn-ghost btn-xs" onClick={() => openEdit(p.id)}>Edit</button>
                          <button className="btn btn-danger btn-xs" onClick={() => remove(p.id)}>Remove</button>
                        </div>
                      </td>
                    </tr>

                    {/* Inline discount editor */}
                    {discountId === p.id && (
                      <tr>
                        <td colSpan={4}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0" }}>
                            <span style={{ fontSize: 13, fontWeight: 600, minWidth: 180 }}>Discount for {p.name}</span>
                            <div className="input-with-addon" style={{ width: 120 }}>
                              <input
                                className="input" style={{ paddingRight: 28 }}
                                value={discountInput} placeholder="0"
                                onChange={e => setDiscountInput(e.target.value)}
                                onKeyDown={e => handleRowKey(e, () => applyDiscount(p.id))}
                                autoFocus
                              />
                              <span className="input-addon">%</span>
                            </div>
                            <button className="btn btn-primary btn-sm" onClick={() => applyDiscount(p.id)}>Apply</button>
                            <button className="btn btn-ghost btn-sm" onClick={() => setDiscountId(null)}>Cancel</button>
                          </div>
                        </td>
                      </tr>
                    )}

                    {/* Inline product editor */}
                    {editingId === p.id && (
                      <tr>
                        <td colSpan={4}>
                          <div style={{ display: "flex", gap: 10, padding: "10px 0", flexWrap: "wrap", alignItems: "center" }}>
                            <input className="input" style={{ flex: "1 1 200px" }} placeholder="Product name" value={editFields.name} onChange={setEdit("name")} onKeyDown={e => handleRowKey(e, () => saveEdit(p.id))} autoFocus />
                            <input className="input" style={{ width: 130 }} placeholder="Price" value={editFields.price} onChange={setEdit("price")} onKeyDown={e => handleRowKey(e, () => saveEdit(p.id))} />
                            <input className="input" style={{ width: 110 }} placeholder="Quantity" value={editFields.quantity} onChange={setEdit("quantity")} onKeyDown={e => handleRowKey(e, () => saveEdit(p.id))} />
                            <input className="input" style={{ width: 100 }} placeholder="Unit" value={editFields.unit} onChange={setEdit("unit")} onKeyDown={e => handleRowKey(e, () => saveEdit(p.id))} />
                            <button className="btn btn-primary btn-sm" onClick={() => saveEdit(p.id)}>Save</button>
                            <button className="btn btn-ghost btn-sm" onClick={() => setEditingId(null)}>Cancel</button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Add product */}
      <div className="card">
        <div className="section-title">Add New Product</div>
        {addError && <div className="alert alert-error" style={{ marginBottom: 14 }}>⚠ {addError}</div>}
        <form onSubmit={handleAdd} style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr auto", gap: 10, alignItems: "end" }}>
          <div className="form-group">
            <label>Product name</label>
            <input className="input" placeholder="e.g. Watermelon" value={newProduct.name} onChange={setNew("name")} />
          </div>
          <div className="form-group">
            <label>Price (₸)</label>
            <input className="input" placeholder="0" value={newProduct.price} onChange={setNew("price")} />
          </div>
          <div className="form-group">
            <label>Quantity</label>
            <input className="input" placeholder="0" value={newProduct.quantity} onChange={setNew("quantity")} />
          </div>
          <div className="form-group">
            <label>Unit</label>
            <input className="input" placeholder="kg / pcs / m" value={newProduct.unit} onChange={setNew("unit")} />
          </div>
          <button type="submit" className="btn btn-primary" style={{ alignSelf: "end" }}>Add product</button>
        </form>
      </div>
    </div>
  );
}
