import React, { useEffect, useState } from "react";import { getLocations, solveTsp } from "./api.js";
import DPProcess from "./components/DPProcess.jsx";
import LocationTable from "./components/LocationTable.jsx";
import MemoTable from "./components/MemoTable.jsx";
import ResultCard from "./components/ResultCard.jsx";
import RouteMap from "./components/RouteMap.jsx";

export default function App() {
  const [locations, setLocations] = useState([]);
  const [distanceMatrix, setDistanceMatrix] = useState([]);
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(1);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDefaultData() {
      try {
        const response = await getLocations();
        setLocations(response.data.locations);
        setDistanceMatrix(response.data.distanceMatrix);
      } catch (err) {
        setError("Backend belum aktif. Jalankan backend terlebih dahulu di port 5000.");
      }
    }

    loadDefaultData();
  }, []);

  const handleSolve = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await solveTsp({ locations, startIndex, endIndex, distanceMatrix });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || "Terjadi kesalahan saat menghitung TSP.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">Perancangan dan Pengembangan Algoritma</p>
          <h1>Visualisasi Dynamic Programming untuk Optimasi Rute Pengantaran Paket</h1>
          <p>
            Aplikasi ini menyelesaikan Travelling Salesman Problem dengan Dynamic Programming dan memoization.
            Kurir berangkat dari titik awal, mengunjungi setiap lokasi tepat satu kali, lalu kembali ke titik awal
            dengan total jarak minimum.
          </p>
        </div>
        <button onClick={handleSolve} disabled={loading || !locations.length}>
          {loading ? "Menghitung..." : "Hitung Rute Optimal"}
        </button>
      </section>

      {error && <div className="alert">{error}</div>}

      <div className="grid two-columns">
        {locations.length > 0 && (
          <LocationTable
            locations={locations}
            startIndex={startIndex}
            setStartIndex={setStartIndex}
            endIndex={endIndex}
            setEndIndex={setEndIndex}
            distanceMatrix={distanceMatrix}
            setDistanceMatrix={setDistanceMatrix}
          />
        )}
        <ResultCard result={result} />
      </div>

      {locations.length > 0 && <RouteMap locations={locations} routeIndexes={result?.routeIndexes} />}
      <MemoTable memoTable={result?.memoTable} />
      <DPProcess steps={result?.steps} explanation={result?.explanation} />
    </main>
  );
}
