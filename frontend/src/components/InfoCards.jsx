import React from "react";

function InfoCard({ icon, title, content, accent }) {
  if (!content) return null;
  return (
    <div className={`info-card accent-${accent}`}>
      <div className="info-card-header">
        <span className="info-icon">{icon}</span>
        <h4 className="info-card-title">{title}</h4>
      </div>
      <p className="info-card-body">{content}</p>
    </div>
  );
}

export default function InfoCards({ data }) {
  return (
    <div className="info-cards-grid">
      <InfoCard
        icon="📋"
        title="Detailed Description"
        content={data.detailed_description}
        accent="blue"
      />
      <InfoCard
        icon="⏱️"
        title="Expected Lifetime"
        content={data.expected_lifetime}
        accent="green"
      />
      <InfoCard
        icon="🛡️"
        title="Maintenance & Safety"
        content={data.maintenance_and_safety}
        accent="yellow"
      />
      <InfoCard
        icon="⚠️"
        title="Failure Symptoms"
        content={data.failure_symptoms}
        accent="red"
      />
    </div>
  );
}