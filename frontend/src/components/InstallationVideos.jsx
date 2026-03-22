import React, { useState } from "react";

export default function InstallationVideos({ videos }) {
  const [active, setActive] = useState(null);

  if (!videos?.length) return null;

  return (
    <div className="videos-section section-card">
      <h3 className="section-title">▶️ Installation Videos</h3>

      {active !== null && (
        <div className="video-embed-wrap">
          <iframe
            className="video-embed"
            src={`https://www.youtube.com/embed/${videos[active].video_id}?autoplay=1`}
            title={videos[active].title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
          <button className="close-video-btn" onClick={() => setActive(null)}>✕ Close</button>
        </div>
      )}

      <div className="video-cards">
        {videos.map((v, i) => (
          <div key={i} className="video-card" onClick={() => setActive(i)}>
            <div className="video-thumb-wrap">
              <img src={v.thumbnail} alt={v.title} className="video-thumb" />
              <div className="play-overlay">▶</div>
            </div>
            <div className="video-info">
              <div className="video-title">{v.title}</div>
              <div className="video-channel">📺 {v.channel}</div>
              {v.description && <div className="video-desc">{v.description}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}