import React from "react";

export default function PartHeader({ data }) {
  return (
    <div className="part-header-card">
      <div className="part-header-left">
        <div className="part-badge">AUTO PART</div>
        <h1 className="part-name">{data.description}</h1>
        <div className="part-meta-row">
          <span className="meta-chip">
            <span className="meta-label">Part #</span>
            <span className="meta-value">{data.part_number}</span>
          </span>
          <span className="meta-chip">
            <span className="meta-label">Manufacturer</span>
            <span className="meta-value">{data.manufacturer_code}</span>
          </span>
        </div>
      </div>
      <div className="part-header-right">
        <div className="price-display">
          <span className="price-label">List Price</span>
          <span className="price-value">${Number(data.price).toFixed(2)}</span>
        </div>
        <div className="ai-badge">
          <span className="ai-dot" />
          AI Researched
        </div>
      </div>
    </div>
  );
}