# visualisasi.py
import folium
import os
import webbrowser
from maps import lokasi
from player import tsp_dp

# Koordinat AKURAT 100% sesuai Google Maps
koordinat_lokasi = {
    0: (-1.277157, 116.830263), # Taman Bekapai
    1: (-1.275529, 116.831518), # Hotel Novotel Balikpapan
    2: (-1.271815, 116.829033), # Hotel Gran Senyiur
    3: (-1.267323, 116.826620)  # SMPN 1 Balikpapan
}

def jalankan_visualisasi_google():
    print("Menghitung rute dengan DP...")
    memo = {}
    total_jarak, rute_indeks = tsp_dp(0, 1, memo)
    
    # 1. Buat Peta Interaktif (Fokus ke area Balikpapan Kota)
    pusat_peta = [-1.2725, 116.8290]
    
    # MENGGUNAKAN SUMBER TAMPILAN GOOGLE MAPS (Bukan OpenStreetMap)
    peta = folium.Map(
        location=pusat_peta, 
        zoom_start=16,
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Maps'
    )
    
    # 2. Tambahkan Pin Lokasi (Marker)
    for i in range(len(lokasi)):
        folium.Marker(
            location=koordinat_lokasi[i],
            popup=f"<b>{lokasi[i]}</b>",
            tooltip=lokasi[i],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(peta)
        
    # 3. Kumpulkan koordinat berdasarkan urutan rute dari algoritma DP
    # (Ini akan menggambar garis tertutup dari titik awal kembali ke titik awal)
    rute_koordinat = [koordinat_lokasi[i] for i in rute_indeks]
    
    # 4. Gambar garis rute lurus antar titik
    folium.PolyLine(
        locations=rute_koordinat,
        color='blue',       
        weight=4,           
        opacity=0.8         
    ).add_to(peta)
    
    # 5. Simpan dan Buka
    nama_file = "peta_rute_tsp_google.html"
    peta.save(nama_file)
    print("Selesai! Membuka peta di browser...")
    
    lokasi_file = 'file://' + os.path.realpath(nama_file)
    webbrowser.open(lokasi_file)

if __name__ == "__main__":
    jalankan_visualisasi_google()