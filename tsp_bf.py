# tsp_bf.py
# Implementasi Travelling Salesman Problem menggunakan Brute Force (Permutasi Lengkap).

from itertools import permutations
from time import perf_counter


def solve_tsp_bf(lokasi, matriks_jarak, start_index=0):
    """
    Menyelesaikan TSP menggunakan metode Brute Force.

    Cara kerja:
    1. Generate semua permutasi lokasi (kecuali titik awal).
    2. Untuk setiap permutasi, hitung total jarak:
       start -> perm[0] -> perm[1] -> ... -> perm[n-1] -> start
    3. Pilih permutasi dengan jarak minimum.

    Kompleksitas waktu: O(n!)
    Cocok untuk jumlah lokasi kecil (≤ 10-12 lokasi).
    """

    jumlah_lokasi = len(lokasi)

    if not isinstance(lokasi, list) or jumlah_lokasi < 2:
        raise ValueError("Minimal harus ada 2 lokasi.")

    if not isinstance(start_index, int) or not (0 <= start_index < jumlah_lokasi):
        raise ValueError("Index titik awal tidak valid.")

    # Daftar index lokasi yang harus dikunjungi (selain titik awal).
    lokasi_lain = [i for i in range(jumlah_lokasi) if i != start_index]

    waktu_mulai = perf_counter()

    jarak_minimum = float("inf")
    rute_terbaik = None
    total_permutasi = 0

    for perm in permutations(lokasi_lain):
        total_permutasi += 1

        # Bangun rute lengkap: start -> permutasi -> kembali ke start.
        rute = [start_index] + list(perm) + [start_index]

        # Hitung total jarak rute ini.
        total_jarak = 0
        for i in range(len(rute) - 1):
            total_jarak += matriks_jarak[rute[i]][rute[i + 1]]

        if total_jarak < jarak_minimum:
            jarak_minimum = total_jarak
            rute_terbaik = rute

    waktu_selesai = perf_counter()

    rute_nama = [lokasi[i] for i in rute_terbaik]

    return {
        "algorithm": "Brute Force",
        "start_index": start_index,
        "start_location": lokasi[start_index],
        "minimum_distance": jarak_minimum,
        "route_indexes": rute_terbaik,
        "route_names": rute_nama,
        "execution_time": waktu_selesai - waktu_mulai,
        "total_permutations": total_permutasi,
    }
