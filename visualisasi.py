# visualisasi.py
# Visualisasi rute TSP menggunakan Folium.

import os
import webbrowser

from maps import koordinat_lokasi, lokasi, matriks_jarak
from tsp_dp import solve_tsp_dp


def buat_peta_rute(hasil, nama_file="peta_rute_tsp.html", buka_browser=True):
    """Membuat peta HTML dengan marker bernomor sesuai urutan rute optimal."""
    try:
        import folium
    except ImportError as exc:
        raise ImportError(
            "Library folium belum terpasang. Jalankan: pip install folium"
        ) from exc

    rute_index = hasil["route_indexes"]
    rute_koordinat = [koordinat_lokasi[i] for i in rute_index]

    pusat_peta = rute_koordinat[0]
    peta = folium.Map(location=pusat_peta, zoom_start=15)

    # Marker bernomor berdasarkan urutan rute.
    # Jika lokasi awal muncul lagi di akhir, marker terakhir tidak ditimpa agar angka awal tetap jelas.
    lokasi_sudah_diberi_marker = set()
    for urutan, index_lokasi in enumerate(rute_index, start=1):
        if index_lokasi in lokasi_sudah_diberi_marker:
            continue

        lokasi_sudah_diberi_marker.add(index_lokasi)
        lat, lon = koordinat_lokasi[index_lokasi]
        nama_lokasi = lokasi[index_lokasi]

        folium.Marker(
            location=(lat, lon),
            popup=f"<b>Urutan {urutan}</b><br>{nama_lokasi}",
            tooltip=f"{urutan}. {nama_lokasi}",
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background:#2563eb;
                    color:white;
                    width:30px;
                    height:30px;
                    border-radius:50%;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-weight:bold;
                    border:3px solid white;
                    box-shadow:0 2px 8px rgba(0,0,0,.35);
                ">{urutan}</div>
                """
            ),
        ).add_to(peta)

    folium.PolyLine(
        locations=rute_koordinat,
        weight=5,
        opacity=0.85,
        tooltip=f"Total jarak: {hasil['minimum_distance']:.2f} km",
    ).add_to(peta)

    peta.save(nama_file)

    if buka_browser:
        webbrowser.open("file://" + os.path.realpath(nama_file))

    return nama_file


if __name__ == "__main__":
    hasil = solve_tsp_dp(lokasi, matriks_jarak, start_index=0)
    file_peta = buat_peta_rute(hasil)
    print(f"Peta berhasil dibuat: {file_peta}")
