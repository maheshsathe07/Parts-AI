import React, { useState } from "react";

const INITIAL = {
  part_number: "",
  description: "",
  manufacturer_code: "",
  price: "",
};

export default function PartForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.part_number || !form.description || !form.manufacturer_code || !form.price) return;
    onSubmit({ ...form, price: parseFloat(form.price) });
  };

  return (
    <div className="form-card">
      <div className="form-header">
        <span className="form-icon">⚙️</span>
        <div>
          <h2 className="form-title">Part Research</h2>
          <p className="form-subtitle">Enter part details to start AI-powered research</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="part-form">
        <div className="form-grid">
          <div className="field">
            <label>Part Number *</label>
            <input
              value={form.part_number}
              onChange={set("part_number")}
              placeholder="e.g. 55555-02180"
              required
            />
          </div>
          <div className="field">
            <label>Manufacturer Code *</label>
            <input
              value={form.manufacturer_code}
              onChange={set("manufacturer_code")}
              placeholder="e.g. TOYOTA, BOSCH"
              required
            />
          </div>
          <div className="field full-width">
            <label>Part Description *</label>
            <input
              value={form.description}
              onChange={set("description")}
              placeholder="e.g. Front Brake Rotor, Oxygen Sensor"
              required
            />
          </div>
          <div className="field">
            <label>Price (USD) *</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.price}
              onChange={set("price")}
              placeholder="e.g. 49.99"
              required
            />
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <span className="btn-loading">
              <span className="spinner" /> Researching Part…
            </span>
          ) : (
            "🔍 Research This Part"
          )}
        </button>
      </form>
    </div>
  );
}