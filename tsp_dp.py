# tsp_dp.py
# Implementasi Travelling Salesman Problem menggunakan Dynamic Programming + Memoization.

from time import perf_counter


def mask_to_binary(mask, jumlah_lokasi):
    """Mengubah visited mask menjadi format biner, misal 0011."""
    return format(mask, f"0{jumlah_lokasi}b")


def validasi_input(lokasi, matriks_jarak, start_index):
    """Validasi data agar program tidak menghitung input yang salah."""
    if not isinstance(lokasi, list) or len(lokasi) < 2:
        raise ValueError("Minimal harus ada 2 lokasi.")

    jumlah_lokasi = len(lokasi)

    if not isinstance(start_index, int) or not (0 <= start_index < jumlah_lokasi):
        raise ValueError("Index titik awal tidak valid.")

    if len(matriks_jarak) != jumlah_lokasi:
        raise ValueError("Ukuran matriks jarak harus sama dengan jumlah lokasi.")

    for i, baris in enumerate(matriks_jarak):
        if len(baris) != jumlah_lokasi:
            raise ValueError("Matriks jarak harus berbentuk persegi.")

        for j, nilai in enumerate(baris):
            if not isinstance(nilai, (int, float)):
                raise ValueError(f"Jarak pada baris {i}, kolom {j} harus berupa angka.")
            if nilai < 0:
                raise ValueError(f"Jarak pada baris {i}, kolom {j} tidak boleh negatif.")


def solve_tsp_dp(lokasi, matriks_jarak, start_index=0):
    """
    Menyelesaikan TSP klasik:
    kurir berangkat dari titik awal, mengunjungi semua lokasi tepat satu kali,
    lalu kembali lagi ke titik awal.

    State DP:
        dp(current_node, visited_mask)

    Makna:
        Jarak minimum dari current_node untuk menyelesaikan kunjungan
        ke semua lokasi yang belum dikunjungi, lalu kembali ke start_index.
    """
    validasi_input(lokasi, matriks_jarak, start_index)

    jumlah_lokasi = len(lokasi)
    semua_terkunjungi = (1 << jumlah_lokasi) - 1
    memo = {}
    pilihan = {}
    langkah = []

    waktu_mulai = perf_counter()

    def dp(current_node, visited_mask):
        state = (current_node, visited_mask)

        # Memoization: jika state pernah dihitung, langsung gunakan hasilnya.
        if state in memo:
            return memo[state]

        # Base case: semua lokasi sudah dikunjungi, maka kembali ke titik awal.
        if visited_mask == semua_terkunjungi:
            hasil = matriks_jarak[current_node][start_index]
            memo[state] = hasil
            pilihan[state] = start_index
            return hasil

        jarak_minimum = float("inf")
        next_terbaik = None
        kandidat_state = []

        # Coba semua lokasi yang belum dikunjungi.
        for next_node in range(jumlah_lokasi):
            sudah_dikunjungi = visited_mask & (1 << next_node)

            if sudah_dikunjungi:
                continue

            mask_baru = visited_mask | (1 << next_node)
            jarak_ke_next = matriks_jarak[current_node][next_node]
            jarak_sisa = dp(next_node, mask_baru)
            total = jarak_ke_next + jarak_sisa

            kandidat_state.append({
                "next_node": next_node,
                "nama_next": lokasi[next_node],
                "rumus": (
                    f"jarak[{current_node}][{next_node}] + "
                    f"dp({next_node}, {mask_to_binary(mask_baru, jumlah_lokasi)})"
                ),
                "jarak_ke_next": jarak_ke_next,
                "jarak_sisa": jarak_sisa,
                "total": total,
            })

            if total < jarak_minimum:
                jarak_minimum = total
                next_terbaik = next_node

        memo[state] = jarak_minimum
        pilihan[state] = next_terbaik

        langkah.append({
            "current_node": current_node,
            "nama_current": lokasi[current_node],
            "visited_mask": mask_to_binary(visited_mask, jumlah_lokasi),
            "kandidat": kandidat_state,
            "dipilih": next_terbaik,
            "nama_dipilih": lokasi[next_terbaik] if next_terbaik is not None else "-",
            "hasil_state": jarak_minimum,
        })

        return jarak_minimum

    # Mask awal: hanya titik awal yang sudah dikunjungi.
    mask_awal = 1 << start_index
    jarak_minimum = dp(start_index, mask_awal)

    waktu_selesai = perf_counter()

    # Rekonstruksi rute dari dictionary pilihan.
    rute_index = [start_index]
    current_node = start_index
    visited_mask = mask_awal

    while visited_mask != semua_terkunjungi:
        state = (current_node, visited_mask)
        next_node = pilihan[state]
        rute_index.append(next_node)
        visited_mask |= 1 << next_node
        current_node = next_node

    # Kembali ke titik awal.
    rute_index.append(start_index)

    rute_nama = [lokasi[i] for i in rute_index]

    # Tabel memo agar mudah dimasukkan ke laporan.
    memo_table = []
    for (node, mask), nilai in sorted(memo.items(), key=lambda item: (item[0][1], item[0][0])):
        memo_table.append({
            "state": f"dp({node}, {mask_to_binary(mask, jumlah_lokasi)})",
            "current_node": lokasi[node],
            "visited_mask": mask_to_binary(mask, jumlah_lokasi),
            "value": nilai,
            "best_next": lokasi[pilihan[(node, mask)]] if (node, mask) in pilihan else "-",
        })

    return {
        "start_index": start_index,
        "start_location": lokasi[start_index],
        "minimum_distance": jarak_minimum,
        "route_indexes": rute_index,
        "route_names": rute_nama,
        "memo_table": memo_table,
        "steps": langkah,
        "execution_time": waktu_selesai - waktu_mulai,
    }
