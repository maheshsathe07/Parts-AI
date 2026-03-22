import React, { useEffect, useState } from "react";

const STEPS = [
  { icon: "🔍", label: "Searching part images…" },
  { icon: "📄", label: "Fetching technical specifications…" },
  { icon: "🚗", label: "Looking up compatible vehicles…" },
  { icon: "⏱️", label: "Checking expected lifetime & maintenance…" },
  { icon: "⚠️", label: "Finding failure symptoms…" },
  { icon: "🔧", label: "Pulling installation steps from OEM sources…" },
  { icon: "▶️", label: "Searching YouTube installation videos…" },
  { icon: "🤖", label: "AI is compiling and structuring all data…" },
];

export default function LoadingOverlay() {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((c) => (c < STEPS.length - 1 ? c + 1 : c));
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="loading-logo">
          <span className="loading-gear">⚙️</span>
        </div>
        <h2 className="loading-title">Researching Part</h2>
        <p className="loading-subtitle">
          AI agent is calling live data sources — this takes about 20–40 seconds
        </p>

        <div className="loading-steps">
          {STEPS.map((step, i) => (
            <div
              key={i}
              className={`loading-step ${i < current ? "done" : ""} ${i === current ? "active" : ""}`}
            >
              <span className="ls-icon">{i < current ? "✅" : step.icon}</span>
              <span className="ls-label">{step.label}</span>
            </div>
          ))}
        </div>

        <div className="loading-bar-track">
          <div
            className="loading-bar-fill"
            style={{ width: `${Math.round(((current + 1) / STEPS.length) * 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}