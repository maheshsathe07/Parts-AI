import React, { useState } from "react";

export default function ImageGallery({ images }) {
  const [active, setActive] = useState(0);

  if (!images?.length) return null;

  return (
    <div className="gallery-section section-card">
      <h3 className="section-title">📸 Part Images</h3>
      <div className="gallery-main">
        <img
          src={images[active].url}
          alt={images[active].title}
          className="gallery-main-img"
          onError={(e) => { e.target.src = "https://via.placeholder.com/600x400?text=Image+Not+Available"; }}
        />
        <div className="gallery-caption">{images[active].title}</div>
      </div>
      <div className="gallery-thumbs">
        {images.map((img, i) => (
          <img
            key={i}
            src={img.url}
            alt={img.title}
            className={`gallery-thumb ${i === active ? "active" : ""}`}
            onClick={() => setActive(i)}
            onError={(e) => { e.target.src = "https://via.placeholder.com/100x80?text=N/A"; }}
          />
        ))}
      </div>
    </div>
  );
}