# main.py
# Program utama TSP Dynamic Programming untuk tugas akhir PPA.

from maps import lokasi, matriks_jarak
from tsp_dp import solve_tsp_dp
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


def tampilkan_hasil(hasil):
    print("=== HASIL RUTE OPTIMAL ===")
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
    print(" TSP Dynamic Programming - Rute Pengantaran")
    print("==============================================")
    print()

    tampilkan_lokasi()
    tampilkan_matriks()

    start_index = input_titik_awal()
    print()

    hasil = solve_tsp_dp(lokasi, matriks_jarak, start_index=start_index)

    tampilkan_hasil(hasil)
    tampilkan_memo(hasil)
    # tampilkan_langkah(hasil)
    print(f"Jumlah state DP yang dihitung: {hasil['state_count']}")
    print()

    kecepatan = input_kecepatan()
    print()

    tampilkan_estimasi_waktu(hasil["minimum_distance"], kecepatan)

    buat_visualisasi = input("Buat visualisasi peta HTML? (y/n): ").strip().lower()
    if buat_visualisasi == "y":
        try:
            nama_file = buat_peta_rute(hasil, buka_browser=True)
            print(f"Peta berhasil dibuat: {nama_file}")
        except ImportError as error:
            print(error)


if __name__ == "__main__":
    main()
