import { defaultLocations as locations, distanceMatrix } from "../data/locations.js";
export function getLocations(req, res) {
  return res.json({
    success: true,
    locations,
    distanceMatrix,
    startIndex: 0,
    endIndex: locations.length - 1,
  });
}

export function solveTsp(req, res) {
  try {
    const { locations, startIndex, endIndex, distanceMatrix } = req.body;

    const validationError = validateInput(locations, startIndex, endIndex, distanceMatrix);
    if (validationError) {
      return res.status(400).json({
        success: false,
        message: validationError,
      });
    }

    const n = locations.length;
    const allVisited = (1 << n) - 1;
    const memo = new Map();
    const choice = new Map();
    const steps = [];
    const memoTable = [];
    const INF = Number.POSITIVE_INFINITY;

    function maskToBinary(mask) {
      return mask.toString(2).padStart(n, "0");
    }

    function getVisitedLocations(mask) {
      return locations.filter((_, index) => mask & (1 << index));
    }

    function dp(currentNode, visitedMask) {
      const key = `${currentNode}-${visitedMask}`;

      if (memo.has(key)) {
        return memo.get(key);
      }

      if (visitedMask === allVisited) {
        const value = currentNode === endIndex ? 0 : INF;

        memo.set(key, value);
        memoTable.push({
          state: `dp[${currentNode}][${maskToBinary(visitedMask)}]`,
          currentNode: locations[currentNode],
          visitedMask: maskToBinary(visitedMask),
          value: Number.isFinite(value) ? Number(value.toFixed(2)) : "∞",
          bestNextNode: currentNode === endIndex ? "Selesai di titik akhir" : "-",
        });

        return value;
      }

      let minDistance = INF;
      let bestNextNode = null;
      const candidates = [];

      for (let nextNode = 0; nextNode < n; nextNode++) {
        const alreadyVisited = visitedMask & (1 << nextNode);

        if (alreadyVisited) continue;

        const newMask = visitedMask | (1 << nextNode);

        const remainingNodesAfterThis = n - countBits(newMask);

        // Titik akhir hanya boleh dikunjungi sebagai lokasi terakhir
        if (nextNode === endIndex && remainingNodesAfterThis > 0) {
          continue;
        }

        const subProblem = dp(nextNode, newMask);
        const total = distanceMatrix[currentNode][nextNode] + subProblem;

        candidates.push({
          nextNode: locations[nextNode],
          calculation: `distance[${currentNode}][${nextNode}] + dp[${nextNode}][${maskToBinary(newMask)}]`,
          distance: distanceMatrix[currentNode][nextNode],
          total: Number.isFinite(total) ? Number(total.toFixed(2)) : "∞",
        });

        if (total < minDistance) {
          minDistance = total;
          bestNextNode = nextNode;
        }
      }

      memo.set(key, minDistance);
      choice.set(key, bestNextNode);

      memoTable.push({
        state: `dp[${currentNode}][${maskToBinary(visitedMask)}]`,
        currentNode: locations[currentNode],
        visitedMask: maskToBinary(visitedMask),
        value: Number.isFinite(minDistance) ? Number(minDistance.toFixed(2)) : "∞",
        bestNextNode: bestNextNode !== null ? locations[bestNextNode] : "-",
      });

      steps.push({
        currentNode: locations[currentNode],
        visitedMask: maskToBinary(visitedMask),
        visitedLocations: getVisitedLocations(visitedMask),
        candidates,
        chosen: bestNextNode !== null ? locations[bestNextNode] : "-",
        result: `dp[${currentNode}][${maskToBinary(visitedMask)}] = ${
          Number.isFinite(minDistance) ? Number(minDistance.toFixed(2)) : "∞"
        }`,
      });

      return minDistance;
    }

    function countBits(mask) {
      let count = 0;
      while (mask > 0) {
        count += mask & 1;
        mask >>= 1;
      }
      return count;
    }

    const startMask = 1 << startIndex;
    const minimumDistance = dp(startIndex, startMask);

    const routeIndexes = buildRoute(startIndex, startMask, choice, allVisited, endIndex);
    const optimalRoute = routeIndexes.map((index) => locations[index]);

    return res.json({
      success: true,
      locations,
      startIndex,
      endIndex,
      startLocation: locations[startIndex],
      endLocation: locations[endIndex],
      optimalRoute,
      routeIndexes,
      minimumDistance: Number(minimumDistance.toFixed(2)),
      memoTable,
      steps,
      explanation: {
        problem:
          "Mencari rute pengantaran paket dari titik awal ke titik akhir dengan mengunjungi semua lokasi tepat satu kali.",
        state: "dp[currentNode][visitedMask]",
        stateMeaning:
          "Jarak minimum dari posisi currentNode menuju titik akhir, dengan kondisi lokasi yang sudah dikunjungi disimpan dalam visitedMask.",
        baseCase:
          "Jika semua lokasi sudah dikunjungi, maka solusi valid hanya jika posisi saat ini adalah titik akhir.",
        transition:
          "dp[current][visited] = min(distance[current][next] + dp[next][visited | (1 << next)])",
        memoization:
          "Hasil setiap state disimpan di memo agar perhitungan submasalah yang sama tidak diulang.",
        note:
          "Titik akhir hanya boleh dikunjungi sebagai lokasi terakhir.",
      },
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: "Terjadi kesalahan pada server.",
      error: error.message,
    });
  }
}

function buildRoute(startIndex, startMask, choice, allVisited, endIndex) {
  const route = [startIndex];
  let currentNode = startIndex;
  let visitedMask = startMask;

  while (visitedMask !== allVisited) {
    const key = `${currentNode}-${visitedMask}`;
    const nextNode = choice.get(key);

    if (nextNode === null || nextNode === undefined) break;

    route.push(nextNode);
    visitedMask |= 1 << nextNode;
    currentNode = nextNode;
  }

  if (route[route.length - 1] !== endIndex) {
    route.push(endIndex);
  }

  return route;
}

function validateInput(locations, startIndex, endIndex, distanceMatrix) {
  if (!Array.isArray(locations)) {
    return "locations harus berupa array.";
  }

  if (locations.length < 2) {
    return "Minimal lokasi adalah 2.";
  }

  if (locations.length > 10) {
    return "Maksimal lokasi adalah 10 agar performa tetap aman.";
  }

  if (!Number.isInteger(startIndex) || startIndex < 0 || startIndex >= locations.length) {
    return "startIndex tidak valid.";
  }

  if (!Number.isInteger(endIndex) || endIndex < 0 || endIndex >= locations.length) {
    return "endIndex tidak valid.";
  }

  if (startIndex === endIndex) {
    return "Titik awal dan titik akhir tidak boleh sama untuk mode rute awal-ke-akhir.";
  }

  if (!Array.isArray(distanceMatrix) || distanceMatrix.length !== locations.length) {
    return "distanceMatrix harus sesuai dengan jumlah lokasi.";
  }

  for (let i = 0; i < distanceMatrix.length; i++) {
    if (!Array.isArray(distanceMatrix[i]) || distanceMatrix[i].length !== locations.length) {
      return "distanceMatrix harus berbentuk matriks persegi.";
    }

    for (let j = 0; j < distanceMatrix[i].length; j++) {
      const value = distanceMatrix[i][j];

      if (typeof value !== "number" || Number.isNaN(value)) {
        return "Semua jarak harus berupa angka.";
      }

      if (value < 0) {
        return "Jarak tidak boleh bernilai negatif.";
      }
    }
  }

  return null;
}