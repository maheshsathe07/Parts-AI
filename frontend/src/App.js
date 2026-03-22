import React, { useState } from "react";
import PartForm from "./components/PartForm";
import PartHeader from "./components/PartHeader";
import ImageGallery from "./components/ImageGallery";
import InfoCards from "./components/InfoCards";
import CompatibleVehicles from "./components/CompatibleVehicles";
import InstallationSteps from "./components/InstallationSteps";
import InstallationVideos from "./components/InstallationVideos";
import Sources from "./components/Sources";
import LoadingOverlay from "./components/LoadingOverlay";
import { researchPart } from "./utils/api";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (part) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await researchPart(part);
      setResult(data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to research part. Please check your API keys and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      {/* ── Top Nav ── */}
      <nav className="topnav">
        <div className="nav-inner">
          <div className="nav-brand">
            <span className="nav-gear">⚙️</span>
            <span className="nav-title">AutoParts<span className="nav-ai">AI</span></span>
          </div>
          <div className="nav-tag">US Market · Groq LLaMA-3 Powered</div>
        </div>
      </nav>

      <main className="main-content">
        {/* ── Hero ── */}
        {!result && !loading && (
          <div className="hero">
            <h1 className="hero-title">
              AI-Powered<br />
              <span className="hero-accent">Parts Research</span>
            </h1>
            <p className="hero-sub">
              Enter any part number and let our AI agent pull real-time data from the web —
              images, specs, compatible vehicles, installation steps, and YouTube tutorials.
            </p>
            <div className="hero-chips">
              <span className="hero-chip">🔍 Google Search</span>
              <span className="hero-chip">▶️ YouTube</span>
              <span className="hero-chip">🤖 Groq LLaMA-3</span>
              <span className="hero-chip">🇺🇸 US Market</span>
            </div>
          </div>
        )}

        {/* ── Form ── */}
        {!result && (
          <PartForm onSubmit={handleSubmit} loading={loading} />
        )}

        {/* ── Error ── */}
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* ── Loading ── */}
        {loading && <LoadingOverlay />}

        {/* ── Results ── */}
        {result && !loading && (
          <div className="results-wrap">
            <button className="back-btn" onClick={handleReset}>
              ← Research Another Part
            </button>

            <PartHeader data={result} />

            <div className="results-main-grid">
              <div className="results-left">
                <ImageGallery images={result.images} />
                <InfoCards data={result} />
              </div>
              <div className="results-right">
                <CompatibleVehicles vehicles={result.compatible_vehicles} />
                <InstallationSteps steps={result.installation_steps} />
              </div>
            </div>

            <InstallationVideos videos={result.installation_videos} />
            <Sources sources={result.sources} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>AutoParts AI · US Market · Data sourced live from the web via Groq LLaMA-3</p>
      </footer>
    </div>
  );
}