# Visualisasi Dynamic Programming untuk Optimasi Rute Pengantaran Paket Menggunakan Travelling Salesman Problem

Project ini adalah aplikasi web fullstack sederhana untuk tugas akhir mata kuliah Perancangan dan Pengembangan Algoritma. Aplikasi digunakan untuk mencari rute pengantaran paket paling optimal dari beberapa lokasi menggunakan algoritma Travelling Salesman Problem dengan Dynamic Programming dan memoization.

Kurir berangkat dari titik awal, mengunjungi semua lokasi tepat satu kali, lalu  ke titik akhir dengan total jarak minimum.

## Masalah yang Diselesaikan

Permasalahan yang diselesaikan adalah optimasi rute pengantaran paket. Jika terdapat beberapa lokasi tujuan, aplikasi akan mencari urutan kunjungan terbaik agar total jarak tempuh menjadi minimum.

Contoh kasus:

- Kurir mulai dari Taman Bekapai.
- Kurir harus mengunjungi Hotel Novotel Balikpapan, Hotel Grand Senyiur Balikpapan, dan SMPN 1 Balikpapan.
- Setelah semua lokasi dikunjungi, kurir ke lokasi terakhir.
- Aplikasi mencari rute dengan jarak paling kecil.

## Konsep Dynamic Programming

Dynamic Programming digunakan karena TSP dapat dipecah menjadi submasalah yang saling berulang. Daripada menghitung ulang submasalah yang sama, hasil perhitungan disimpan di memo.

### State DP

```text
dp[currentNode][visitedMask]
```

Artinya:

> Jarak minimum untuk menyelesaikan perjalanan dari posisi `currentNode`, dengan kondisi lokasi yang sudah dikunjungi direpresentasikan oleh `visitedMask`.

### Base Case

```text
Jika semua lokasi sudah dikunjungi, maka kembali ke titik awal.
```

Dalam kode:

```text
if visitedMask == allVisited:
    return distance[currentNode][startIndex]
```

### Transition

```text
dp[current][visited] = min(distance[current][next] + dp[next][visited | (1 << next)])
```

Untuk setiap `next` yang belum dikunjungi, algoritma mencoba berpindah ke lokasi tersebut, lalu memilih total jarak paling kecil.

## Penjelasan Bitmask

Bitmask digunakan untuk menyimpan status lokasi yang sudah dikunjungi.

Contoh jika ada 4 lokasi:

```text
0001 = lokasi 0 sudah dikunjungi
0011 = lokasi 0 dan 1 sudah dikunjungi
1111 = semua lokasi sudah dikunjungi
```

Operasi penting:

```text
visitedMask | (1 << next)
```

Artinya menambahkan lokasi `next` ke daftar lokasi yang sudah dikunjungi.

## Penjelasan Memoization

Memoization menyimpan hasil perhitungan setiap state agar tidak dihitung ulang.

Contoh key memo:

```text
memo["0-0001"] = 5.20
```

Artinya nilai minimum dari node 0 dengan visited mask 0001 adalah 5.20 km.

## Struktur Folder

```text
tsp-dp-route-optimizer/
├── backend/
│   ├── package.json
│   └── src/
│       ├── server.js
│       ├── data/
│       │   └── locations.js
│       ├── controllers/
│       │   └── tspController.js
│       └── routes/
│           └── tspRoutes.js
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── components/
│       │   ├── LocationTable.jsx
│       │   ├── ResultCard.jsx
│       │   ├── DPProcess.jsx
│       │   ├── MemoTable.jsx
│       │   └── RouteMap.jsx
│       └── styles.css
└── README.md
```

## Endpoint Backend

### GET `/api/locations`

Mengembalikan daftar lokasi default, matriks jarak default, dan koordinat sederhana untuk visualisasi.

### POST `/api/tsp/solve`

Menghitung rute optimal menggunakan Dynamic Programming.

Contoh request:

```json
{
  "locations": [
    "Taman Bekapai",
    "Hotel Novotel Balikpapan",
    "Hotel Grand Senyiur Balikpapan",
    "SMPN 1 Balikpapan"
  ],
  "startIndex": 0,
  "distanceMatrix": [
    [0, 0.5, 1.2, 2.5],
    [0.5, 0, 0.8, 2.0],
    [1.2, 0.8, 0, 1.5],
    [2.5, 2.0, 1.5, 0]
  ]
}
```

Contoh output utama:

```text
Rute optimal:
Taman Bekapai -> Hotel Novotel Balikpapan -> SMPN 1 Balikpapan -> Hotel Grand Senyiur Balikpapan -> Taman Bekapai

Total jarak:
5.20 km
```

## Cara Menjalankan Backend

```bash
cd backend
npm install
npm run dev
```

Backend berjalan di:

```text
http://localhost:5000
```

## Cara Menjalankan Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend berjalan di:

```text
http://localhost:5173
```

## Validasi Backend

Backend sudah memvalidasi:

- `locations` harus berupa array.
- `distanceMatrix` harus berbentuk matriks persegi.
- Jumlah `locations` harus sama dengan ukuran `distanceMatrix`.
- `startIndex` harus valid.
- Jarak tidak boleh bernilai negatif.
- Minimal lokasi adalah 2.
- Maksimal lokasi adalah 10 agar performa tetap aman.

## Fitur Frontend

- Menampilkan judul aplikasi.
- Menampilkan penjelasan TSP dan Dynamic Programming.
- Menampilkan daftar lokasi default Balikpapan.
- User bisa memilih titik awal.
- User bisa mengubah matriks jarak.
- Tombol untuk menghitung rute optimal.
- Menampilkan rute optimal dan total jarak minimum.
- Menampilkan tabel memo DP.
- Menampilkan langkah-langkah proses Dynamic Programming.
- Menampilkan penjelasan masalah besar, submasalah, state, base case, transition, bitmask, dan memoization.
- Menampilkan visualisasi rute sederhana menggunakan SVG.

## Kesimpulan

Project ini menunjukkan penerapan Dynamic Programming pada Travelling Salesman Problem. Dengan state `dp[currentNode][visitedMask]`, aplikasi dapat memecah masalah besar menjadi submasalah, menyimpan hasilnya menggunakan memoization, dan menemukan rute pengantaran paket dengan total jarak minimum.
