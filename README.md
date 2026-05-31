# Visualisasi Dynamic Programming untuk Optimasi Rute Pengantaran Paket Menggunakan TSP

## Deskripsi
Project ini menyelesaikan masalah optimasi rute pengantaran paket menggunakan Travelling Salesman Problem (TSP) dengan Dynamic Programming dan memoization.

Kurir berangkat dari satu titik awal, mengunjungi semua lokasi tepat satu kali, lalu kembali ke titik awal dengan total jarak minimum.

## Bahasa dan Library
- Bahasa: Python
- Library utama: standar Python
- Library opsional visualisasi: folium

## Konsep Dynamic Programming
State yang digunakan:

```text
dp(current_node, visited_mask)
```

Artinya jarak minimum dari posisi `current_node` dengan kondisi lokasi yang sudah dikunjungi direpresentasikan oleh `visited_mask`.

## Base Case
Jika semua lokasi sudah dikunjungi, maka kurir kembali ke titik awal:

```text
return distance[current_node][start_index]
```

## Transisi
Untuk setiap lokasi berikutnya yang belum dikunjungi:

```text
dp(current, visited) = min(distance[current][next] + dp(next, visited | (1 << next)))
```

## Bitmask
Bitmask digunakan untuk menandai lokasi yang sudah dikunjungi.

Contoh untuk 4 lokasi:

```text
0001 = lokasi 0 sudah dikunjungi
0011 = lokasi 0 dan 1 sudah dikunjungi
1111 = semua lokasi sudah dikunjungi
```

## Cara Menjalankan
Install library visualisasi terlebih dahulu jika ingin membuat peta:

```bash
pip install -r requirements.txt
```

Jalankan program utama:

```bash
python main.py
```

## File Penting
- `maps.py`: data lokasi, koordinat, dan matriks jarak.
- `tsp_dp.py`: implementasi algoritma TSP Dynamic Programming.
- `visualisasi.py`: visualisasi peta rute menggunakan Folium.
- `main.py`: program utama berbasis terminal.

## Kompleksitas
Jumlah lokasi = n.

- Kompleksitas waktu: O(n^2 * 2^n)
- Kompleksitas ruang: O(n * 2^n)

## Kesimpulan
Dynamic Programming dapat digunakan untuk menyelesaikan TSP dengan lebih efisien dibanding brute force murni, karena hasil submasalah disimpan dalam memo sehingga tidak dihitung berulang.
