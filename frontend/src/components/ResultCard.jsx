import React from "react";
export default function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="card result-empty">
        <p className="eyebrow">Output</p>
        <h2>Hasil rute optimal akan tampil di sini</h2>
        <p>Klik tombol hitung untuk menjalankan algoritma TSP Dynamic Programming.</p>
      </section>
    );
  }

  return (
    <section className="card result-card">
      <p className="eyebrow">Output</p>
      <h2>Rute Optimal</h2>
      <div className="distance-box">
        <span>Total Jarak Minimum</span>
        <strong>{result.minimumDistance.toFixed(2)} km</strong>
      </div>
      <div className="route-chain">
        {result.optimalRoute.map((location, index) => (
          <span key={`${location}-${index}`}>
            {location}
            {index < result.optimalRoute.length - 1 && <b>→</b>}
          </span>
        ))}
      </div>
      <ol className="route-list">
        {result.optimalRoute.map((location, index) => (
          <li key={`${location}-ordered-${index}`}>{location}</li>
        ))}
      </ol>
    </section>
  );
}
