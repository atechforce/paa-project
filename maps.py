# maps.py
# Data lokasi, koordinat, dan matriks jarak untuk studi kasus TSP.

lokasi = [
    "Taman Bekapai",
    "Hotel Novotel Balikpapan",
    "Hotel Grand Senyiur Balikpapan",
    "SMPN 1 Balikpapan",
    "Balikpapan Plaza",
    "Pantai Kemala",
]

# Koordinat digunakan untuk visualisasi peta Folium.
# Format: index_lokasi: (latitude, longitude)
koordinat_lokasi = {
    0: (-1.277157, 116.830263),  # Taman Bekapai
    1: (-1.275529, 116.831518),  # Hotel Novotel Balikpapan
    2: (-1.271815, 116.829033),  # Hotel Grand Senyiur Balikpapan
    3: (-1.267323, 116.826620),  # SMPN 1 Balikpapan
    4: (-1.276620, 116.827100),  # Balikpapan Plaza
    5: (-1.279250, 116.824550),  # Pantai Kemala
}

# Matriks jarak antar lokasi dalam satuan kilometer.
# Baris dan kolom mengikuti urutan list lokasi.
# Contoh: matriks_jarak[0][1] berarti jarak Taman Bekapai ke Hotel Novotel.
matriks_jarak = [
    [0.0, 0.5, 1.2, 2.5, 0.8, 1.6],
    [0.5, 0.0, 0.8, 2.0, 0.7, 1.8],
    [1.2, 0.8, 0.0, 1.5, 1.4, 2.4],
    [2.5, 2.0, 1.5, 0.0, 2.8, 3.5],
    [0.8, 0.7, 1.4, 2.8, 0.0, 1.2],
    [1.6, 1.8, 2.4, 3.5, 1.2, 0.0],
]
