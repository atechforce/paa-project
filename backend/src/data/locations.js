export const defaultLocations = [
  "Taman Bekapai",
  "Hotel Novotel Balikpapan",
  "Hotel Grand Senyiur Balikpapan",
  "SMPN 1 Balikpapan",
  "Balikpapan Plaza",
  "E-Walk Balikpapan",
  "Pantai Kemala"
];

// Matriks ini mengikuti data project Python awal agar hasil default = 5.20 km.
export const distanceMatrix = [
  [0, 1.2, 2.1, 3.5, 0.8, 4.2, 2.7],
  [1.2, 0, 1.4, 2.0, 1.0, 3.6, 2.5],
  [2.1, 1.4, 0, 1.6, 1.8, 3.2, 2.9],
  [3.5, 2.0, 1.6, 0, 2.9, 2.7, 3.8],
  [0.8, 1.0, 1.8, 2.9, 0, 3.9, 2.1],
  [4.2, 3.6, 3.2, 2.7, 3.9, 0, 5.0],
  [2.7, 2.5, 2.9, 3.8, 2.1, 5.0, 0]
];

export const defaultCoordinates = [
  { x: 18, y: 72 },
  { x: 44, y: 45 },
  { x: 72, y: 58 },
  { x: 84, y: 22 }
];
