import React from "react";

export default function LocationTable({
  locations,
  startIndex,
  setStartIndex,
  endIndex,
  setEndIndex,
  distanceMatrix,
  setDistanceMatrix,
}) {
  const updateDistance = (rowIndex, colIndex, value) => {
    const nextMatrix = distanceMatrix.map((row) => [...row]);
    const parsedValue = value === "" ? "" : Number(value);

    nextMatrix[rowIndex][colIndex] = parsedValue;

    // Karena jarak antar lokasi bersifat dua arah, mirror otomatis agar matriks tetap simetris.
    if (rowIndex !== colIndex) {
      nextMatrix[colIndex][rowIndex] = parsedValue;
    }

    setDistanceMatrix(nextMatrix);
  };

  const handleStartChange = (value) => {
    const newStartIndex = Number(value);
    setStartIndex(newStartIndex);

    // Kalau titik awal baru sama dengan titik akhir, pindahkan titik akhir ke lokasi lain.
    if (newStartIndex === endIndex) {
      const nextEndIndex = locations.findIndex((_, index) => index !== newStartIndex);
      setEndIndex(nextEndIndex);
    }
  };

  const handleEndChange = (value) => {
    setEndIndex(Number(value));
  };

  return (
    <section className="card wide-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">Input Data</p>
          <h2>Lokasi dan Matriks Jarak</h2>
        </div>

        <div className="form-group">
          <label>Titik Awal</label>
          <select
            value={startIndex}
            onChange={(event) => handleStartChange(event.target.value)}
          >
            {locations.map((location, index) => (
              <option key={location} value={index}>
                {location}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Titik Akhir</label>
          <select
            value={endIndex}
            onChange={(event) => handleEndChange(event.target.value)}
          >
            {locations.map((location, index) => (
              <option key={location} value={index} disabled={index === startIndex}>
                {location}
              </option>
            ))}
          </select>
          <small>
            Kurir akan berhenti di titik akhir ini setelah semua lokasi dikunjungi.
          </small>
        </div>
      </div>

      <div className="location-list">
        {locations.map((location, index) => (
          <div className="location-pill" key={location}>
            <span>{index}</span>
            {location}
          </div>
        ))}
      </div>

      <div className="matrix-wrapper">
        <table className="matrix-table">
          <thead>
            <tr>
              <th>Lokasi</th>
              {locations.map((_, index) => (
                <th key={index}>L{index}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {distanceMatrix.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <th>L{rowIndex}</th>
                {row.map((value, colIndex) => (
                  <td key={`${rowIndex}-${colIndex}`}>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      disabled={rowIndex === colIndex}
                      value={value}
                      onChange={(event) =>
                        updateDistance(rowIndex, colIndex, event.target.value)
                      }
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}