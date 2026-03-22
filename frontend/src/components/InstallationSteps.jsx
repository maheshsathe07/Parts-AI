import React from "react";

export default function InstallationSteps({ steps }) {
  if (!steps?.length) return null;

  return (
    <div className="steps-section section-card">
      <h3 className="section-title">🔧 Installation Steps</h3>
      <ol className="steps-list">
        {steps.map((step, i) => {
          // Strip leading "Step N:" prefix if LLM included it
          const clean = step.replace(/^step\s*\d+[:\-\.]?\s*/i, "");
          return (
            <li key={i} className="step-item">
              <span className="step-num">{i + 1}</span>
              <span className="step-text">{clean}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}