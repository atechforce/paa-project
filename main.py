# main.py
# Program utama TSP Dynamic Programming & Brute Force untuk tugas akhir PPA.

from maps import lokasi, matriks_jarak
from tsp_dp import solve_tsp_dp
from tsp_bf import solve_tsp_bf
from visualisasi import buat_peta_rute


def tampilkan_lokasi():
    print("Daftar Lokasi:")
    for i, nama in enumerate(lokasi):
        print(f"  L{i} = {nama}")
    print()


def tampilkan_matriks():
    print("Matriks Jarak (km):")
    header = "      " + " ".join([f"L{i:>6}" for i in range(len(lokasi))])
    print(header)
    for i, baris in enumerate(matriks_jarak):
        isi_baris = " ".join([f"{nilai:>7.1f}" for nilai in baris])
        print(f"L{i:<3} {isi_baris}")
    print()


def tampilkan_hasil(hasil, label=""):
    prefix = f" ({label})" if label else ""
    print(f"=== HASIL RUTE OPTIMAL{prefix} ===")
    print(f"Algoritma         : {hasil.get('algorithm', 'Dynamic Programming')}")
    print(f"Titik Awal        : {hasil['start_location']}")
    print(f"Rute Optimal      : {' -> '.join(hasil['route_names'])}")
    print(f"Total Jarak       : {hasil['minimum_distance']:.2f} km")
    print(f"Waktu Eksekusi    : {hasil['execution_time']:.8f} detik")
    print()


def tampilkan_memo(hasil, batas=20):
    print("=== TABEL MEMO DP ===")
    print(f"{'State':<18} {'Current Node':<35} {'Value':>10} {'Best Next':<35}")
    print("-" * 105)

    for item in hasil["memo_table"][:batas]:
        print(
            f"{item['state']:<18} "
            f"{item['current_node']:<35} "
            f"{item['value']:>10.2f} "
            f"{item['best_next']:<35}"
        )

    if len(hasil["memo_table"]) > batas:
        print(f"... {len(hasil['memo_table']) - batas} state lainnya tidak ditampilkan.")
    print()


# def tampilkan_langkah(hasil, batas=8):
#     print("=== CONTOH LANGKAH PERHITUNGAN DP ===")
#     for nomor, step in enumerate(hasil["steps"][:batas], start=1):
#         print(f"Step {nomor}")
#         print(f"  Current Node : {step['nama_current']}")
#         print(f"  Visited Mask : {step['visited_mask']}")
#         print(f"  Dipilih      : {step['nama_dipilih']}")
#         print(f"  Hasil State  : {step['hasil_state']:.2f} km")
#         print()

    # if len(hasil["steps"]) > batas:
    #     print(f"... {len(hasil['steps']) - batas} langkah lainnya tidak ditampilkan.")
    # print()


def tampilkan_perbandingan(hasil_dp, hasil_bf):
    """Menampilkan tabel perbandingan antara algoritma DP dan Brute Force."""
    print("=" * 75)
    print("              PERBANDINGAN ALGORITMA DP vs BRUTE FORCE")
    print("=" * 75)

    rute_dp = " -> ".join([f"L{i}" for i in hasil_dp["route_indexes"]])
    rute_bf = " -> ".join([f"L{i}" for i in hasil_bf["route_indexes"]])

    rute_sama = hasil_dp["route_indexes"] == hasil_bf["route_indexes"]

    print(f"{'Kriteria':<22} {'Dynamic Programming':<28} {'Brute Force':<28}")
    print("-" * 75)
    print(f"{'Total Jarak':<22} {hasil_dp['minimum_distance']:<28.2f} {hasil_bf['minimum_distance']:<28.2f}")
    print(f"{'Waktu Eksekusi':<22} {hasil_dp['execution_time']:<28.8f} {hasil_bf['execution_time']:<28.8f}")
    print(f"{'Jumlah Operasi':<22} {str(hasil_dp['state_count']) + ' state':<28} {str(hasil_bf['total_permutations']) + ' permutasi':<28}")
    print(f"{'Rute Optimal':<22} {rute_dp:<28} {rute_bf:<28}")
    print(f"{'Rute Sama?':<22} {'Ya (V)' if rute_sama else 'Tidak (X)'}")

    # Hitung speedup
    if hasil_bf["execution_time"] > 0:
        speedup = hasil_bf["execution_time"] / hasil_dp["execution_time"]
        print(f"{'Speedup DP':<22} {speedup:.2f}x lebih cepat dari Brute Force")

    print()


def input_titik_awal():
    while True:
        pilihan = input("Pilih titik awal berdasarkan nomor lokasi, default 0: ").strip()

        if pilihan == "":
            return 0

        try:
            index = int(pilihan)
            if 0 <= index < len(lokasi):
                return index
            print("Nomor lokasi tidak valid.")
        except ValueError:
            print("Input harus berupa angka.")


def input_kecepatan():
    """Meminta input kecepatan salesman dalam km/jam."""
    while True:
        pilihan = input("Masukkan kecepatan salesman (km/jam), default 40: ").strip()

        if pilihan == "":
            return 40.0

        try:
            kecepatan = float(pilihan)
            if kecepatan > 0:
                return kecepatan
            print("Kecepatan harus lebih dari 0.")
        except ValueError:
            print("Input harus berupa angka.")


def tampilkan_estimasi_waktu(total_jarak, kecepatan):
    """Menghitung dan menampilkan estimasi waktu tempuh salesman."""
    waktu_jam = total_jarak / kecepatan
    waktu_menit = waktu_jam * 60

    jam = int(waktu_menit // 60)
    menit = int(waktu_menit % 60)
    detik = int((waktu_menit % 1) * 60)

    print("=== ESTIMASI WAKTU TEMPUH ===")
    print(f"Total Jarak       : {total_jarak:.2f} km")
    print(f"Kecepatan         : {kecepatan:.1f} km/jam")
    print(f"Estimasi Waktu    : {waktu_jam:.4f} jam ({waktu_menit:.2f} menit)")

    if jam > 0:
        print(f"                  : {jam} jam {menit} menit {detik} detik")
    else:
        print(f"                  : {menit} menit {detik} detik")

    print()


def main():
    print("==============================================")
    print(" TSP - Rute Pengantaran Optimal")
    print(" Dynamic Programming vs Brute Force")
    print("==============================================")
    print()

    tampilkan_lokasi()
    tampilkan_matriks()

    start_index = input_titik_awal()
    print()

    # === Jalankan algoritma Dynamic Programming ===
    print("Menjalankan algoritma Dynamic Programming...")
    hasil_dp = solve_tsp_dp(lokasi, matriks_jarak, start_index=start_index)
    hasil_dp["algorithm"] = "Dynamic Programming"
    tampilkan_hasil(hasil_dp, "Dynamic Programming")
    tampilkan_memo(hasil_dp)
    print(f"Jumlah state DP yang dihitung: {hasil_dp['state_count']}")
    print()

    # === Jalankan algoritma Brute Force ===
    print("Menjalankan algoritma Brute Force...")
    hasil_bf = solve_tsp_bf(lokasi, matriks_jarak, start_index=start_index)
    tampilkan_hasil(hasil_bf, "Brute Force")
    print(f"Jumlah permutasi yang dievaluasi: {hasil_bf['total_permutations']}")
    print()

    # === Tampilkan perbandingan ===
    tampilkan_perbandingan(hasil_dp, hasil_bf)

    # === Input kecepatan dan estimasi waktu ===
    kecepatan = input_kecepatan()
    print()

    tampilkan_estimasi_waktu(hasil_dp["minimum_distance"], kecepatan)

    # === Visualisasi ===
    buat_visualisasi = input("Buat visualisasi peta HTML? (y/n): ").strip().lower()
    if buat_visualisasi == "y":
        try:
            nama_file = buat_peta_rute(
                hasil_dp,
                hasil_bf=hasil_bf,
                buka_browser=True
            )
            print(f"Peta berhasil dibuat: {nama_file}")
        except ImportError as error:
            print(error)


if __name__ == "__main__":
    main()

