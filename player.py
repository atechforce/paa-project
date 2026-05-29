# player.py
import time
from maps import lokasi, matriks_jarak

def tsp_dp(current_node, visited_mask, memo):
    jumlah_lokasi = len(lokasi)
    
    # Base Case: Jika semua lokasi sudah dikunjungi
    # (1 << jumlah_lokasi) - 1 akan menghasilkan nilai biner dimana semua bit adalah 1 (misal 4 lokasi = 1111)
    if visited_mask == (1 << jumlah_lokasi) - 1:
        # Kembalikan jarak dari lokasi saat ini kembali ke titik start (node 0) 
        # beserta rutenya
        return matriks_jarak[current_node][0], [current_node, 0]

    # Cek Memoization: Apakah state ini sudah pernah dihitung sebelumnya?
    state = (current_node, visited_mask)
    if state in memo:
        return memo[state]

    min_jarak = float('inf')
    rute_terbaik = []

    # Coba kunjungi semua lokasi yang belum dikunjungi
    for next_node in range(jumlah_lokasi):
        # Operasi bitwise AND untuk mengecek apakah next_node belum ada di visited_mask
        if not (visited_mask & (1 << next_node)):
            # Rekursi ke node selanjutnya dengan memperbarui visited_mask
            jarak_selanjutnya, path = tsp_dp(next_node, visited_mask | (1 << next_node), memo)
            total_jarak = matriks_jarak[current_node][next_node] + jarak_selanjutnya
            
            # Cari rute dengan jarak paling minimal
            if total_jarak < min_jarak:
                min_jarak = total_jarak
                rute_terbaik = [current_node] + path

    # Simpan hasil ke dalam memory (memoization)
    memo[state] = (min_jarak, rute_terbaik)
    return memo[state]

if __name__ == "__main__":
    print("=== Simulasi Pengantaran Paket (TSP Dynamic Programming) ===\n")
    
    # Menyiapkan dictionary untuk memoization
    memo = {}
    
    # Mulai menghitung waktu
    mulai_waktu = time.time()
    
    # Kita mulai dari Taman Bekapai (Indeks 0). 
    # Mask awal adalah 1 (0001 dalam biner) menandakan node 0 sudah dikunjungi.
    total_jarak, rute_indeks = tsp_dp(0, 1, memo)
    
    # Berhenti menghitung waktu
    selesai_waktu = time.time()
    waktu_eksekusi = selesai_waktu - mulai_waktu

    # Menerjemahkan array indeks menjadi nama lokasi yang bisa dibaca
    rute_nama = [lokasi[i] for i in rute_indeks]
    rute_teks = " -> ".join(rute_nama)

    print(f"Rute Paling Optimal : {rute_teks}")
    print(f"Total Jarak Tempuh  : {total_jarak:.2f} km")
    print(f"Waktu Eksekusi      : {waktu_eksekusi:.6f} detik")