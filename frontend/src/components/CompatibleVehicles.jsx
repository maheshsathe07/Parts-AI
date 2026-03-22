import React, { useState } from "react";

export default function CompatibleVehicles({ vehicles }) {
  const [search, setSearch] = useState("");

  if (!vehicles?.length) return null;

  const filtered = vehicles.filter(
    (v) =>
      !search ||
      `${v.year} ${v.make} ${v.model} ${v.trim || ""}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="vehicles-section section-card">
      <h3 className="section-title">🚗 Compatible Vehicles</h3>
      <input
        className="vehicle-search"
        placeholder="Filter by year, make, or model…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div className="vehicles-table-wrap">
        <table className="vehicles-table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Make</th>
              <th>Model</th>
              <th>Trim</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((v, i) => (
              <tr key={i}>
                <td className="year-cell">{v.year}</td>
                <td>{v.make}</td>
                <td>{v.model}</td>
                <td className="trim-cell">{v.trim || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="vehicle-count">{filtered.length} vehicle(s) listed</div>
    </div>
  );
}