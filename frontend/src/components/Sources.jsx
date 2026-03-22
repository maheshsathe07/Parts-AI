import React, { useState } from "react";

export default function Sources({ sources }) {
  const [open, setOpen] = useState(false);
  const unique = [...new Set((sources || []).filter(Boolean))];
  if (!unique.length) return null;

  return (
    <div className="sources-section section-card">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        🔗 {open ? "Hide" : "Show"} Sources ({unique.length})
      </button>
      {open && (
        <ul className="sources-list">
          {unique.map((src, i) => (
            <li key={i}>
              <a href={src} target="_blank" rel="noopener noreferrer" className="source-link">
                {src}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}