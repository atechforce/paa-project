import React from "react";

function formatNumber(value) {
  if (value === undefined || value === null) return "-";
  if (value === "∞") return "∞";
  if (typeof value === "number") return value.toFixed(2);
  return value;
}

export default function DPProcess({ steps, explanation }) {
  if (!steps || steps.length === 0) {
    return (
      <section className="card">
        <div className="section-title">
          <div>
            <p className="eyebrow">Proses Dynamic Programming</p>
            <h2>Langkah Perhitungan DP</h2>
          </div>
        </div>
        <p className="muted">
          Klik tombol <strong>Hitung Rute Optimal</strong> untuk melihat proses perhitungan Dynamic Programming.
        </p>
      </section>
    );
  }

  return (
    <section className="card">
      <div className="section-title">
        <div>
          <p className="eyebrow">Proses Dynamic Programming</p>
          <h2>Langkah Perhitungan DP</h2>
        </div>
      </div>

      {explanation && (
        <div className="explanation-box">
          <h3>Penjelasan Konsep</h3>

          {explanation.problem && (
            <p>
              <strong>Masalah:</strong> {explanation.problem}
            </p>
          )}

          <p>
            <strong>State:</strong> {explanation.state}
          </p>

          {explanation.stateMeaning && (
            <p>
              <strong>Makna State:</strong> {explanation.stateMeaning}
            </p>
          )}

          <p>
            <strong>Base Case:</strong> {explanation.baseCase}
          </p>

          <p>
            <strong>Transition:</strong> {explanation.transition}
          </p>

          <p>
            <strong>Memoization:</strong> {explanation.memoization}
          </p>

          {explanation.note && (
            <p>
              <strong>Catatan:</strong> {explanation.note}
            </p>
          )}
        </div>
      )}

      <div className="steps-list">
        {steps.map((step, index) => (
          <div className="step-card" key={`${step.currentNode}-${step.visitedMask}-${index}`}>
            <div className="step-header">
              <span>Step {index + 1}</span>
              <strong>{step.currentNode}</strong>
            </div>

            <p>
              <strong>Visited Mask:</strong> {step.visitedMask}
            </p>

            <p>
              <strong>Lokasi Dikunjungi:</strong>{" "}
              {step.visitedLocations?.join(", ") || "-"}
            </p>

            <div className="candidate-list">
              <strong>Kandidat:</strong>

              {step.candidates && step.candidates.length > 0 ? (
                step.candidates.map((candidate, candidateIndex) => (
                  <div className="candidate-item" key={candidateIndex}>
                    <p>
                      <strong>Next:</strong> {candidate.nextNode}
                    </p>
                    <p>
                      <strong>Rumus:</strong> {candidate.calculation}
                    </p>
                    <p>
                      <strong>Jarak:</strong> {formatNumber(candidate.distance)} km
                    </p>
                    <p>
                      <strong>Total:</strong> {formatNumber(candidate.total)} km
                    </p>
                  </div>
                ))
              ) : (
                <p className="muted">Tidak ada kandidat.</p>
              )}
            </div>

            <p>
              <strong>Dipilih:</strong> {step.chosen || "-"}
            </p>

            <p>
              <strong>Hasil:</strong> {step.result || "-"}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}