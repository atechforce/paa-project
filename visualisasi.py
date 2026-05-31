# visualisasi.py
# Membuat visualisasi rute TSP pada peta HTML menggunakan Folium.
# Garis rute dibuat mengikuti jalan menggunakan OSRM jika internet tersedia.
# Jika OSRM gagal, program otomatis memakai garis lurus sebagai cadangan.

import webbrowser
import requests
import folium
from maps import lokasi, koordinat


def ambil_rute_jalan_osrm(titik_awal, titik_tujuan):
    """
    Mengambil koordinat jalur jalan dari OSRM.

    Parameter:
    titik_awal  : tuple (latitude, longitude)
    titik_tujuan: tuple (latitude, longitude)

    OSRM membutuhkan format longitude,latitude.
    Folium membutuhkan format latitude,longitude.
    """

    lat1, lon1 = titik_awal
    lat2, lon2 = titik_tujuan

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}"
        "?overview=full&geometries=geojson"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("OSRM gagal mendapatkan rute jalan.")

    koordinat_osrm = data["routes"][0]["geometry"]["coordinates"]

    # OSRM mengembalikan [longitude, latitude]
    # Folium membutuhkan [latitude, longitude]
    return [(lat, lon) for lon, lat in koordinat_osrm]


def buat_marker_angka(label):
    """
    Membuat marker custom berbentuk lingkaran biru dengan angka urutan rute.
    Contoh label:
    - "1"
    - "2"
    - "1/8" untuk titik awal sekaligus titik akhir
    """

    return folium.DivIcon(
        html=f"""
        <div style="
            background-color:#2563eb;
            color:white;
            min-width:34px;
            height:34px;
            padding:0 6px;
            border-radius:999px;
            text-align:center;
            line-height:34px;
            font-weight:bold;
            border:3px solid white;
            box-shadow:0 2px 8px rgba(0,0,0,0.35);
            font-size:13px;
            font-family:Arial, sans-serif;
        ">
            {label}
        </div>
        """
    )


def buat_peta_rute(hasil, nama_file="peta_rute_tsp.html", buka_browser=False):
    """
    Membuat file HTML berisi peta rute optimal.

    Parameter:
    hasil:
        dictionary hasil dari solve_tsp_dp()
        harus memiliki key "route_indexes"

    nama_file:
        nama file HTML output

    buka_browser:
        jika True, file HTML langsung dibuka di browser
    """

    route_indexes = hasil["route_indexes"]

    if not route_indexes:
        raise ValueError("Route indexes kosong. Tidak dapat membuat peta.")

    titik_awal = koordinat[route_indexes[0]]

    peta = folium.Map(
        location=titik_awal,
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    # ==========================================================
    # MARKER ANGKA URUTAN
    # ==========================================================
    # Pada TSP klasik, titik awal muncul dua kali:
    # contoh: L0 -> L4 -> L2 -> L1 -> L0
    # Jika marker digambar satu per satu, marker terakhir akan menimpa marker 1.
    # Maka urutan lokasi yang sama digabung menjadi "1/akhir".
    # ==========================================================

    marker_urutan = {}

    for urutan, index_lokasi in enumerate(route_indexes, start=1):
        if index_lokasi not in marker_urutan:
            marker_urutan[index_lokasi] = [urutan]
        else:
            marker_urutan[index_lokasi].append(urutan)

    for index_lokasi, daftar_urutan in marker_urutan.items():
        nama_lokasi = lokasi[index_lokasi]
        lat, lon = koordinat[index_lokasi]

        label_urutan = "/".join(map(str, daftar_urutan))

        folium.Marker(
            location=[lat, lon],
            popup=f"Urutan {label_urutan}: {nama_lokasi}",
            tooltip=f"Urutan {label_urutan}: {nama_lokasi}",
            icon=buat_marker_angka(label_urutan)
        ).add_to(peta)

    # ==========================================================
    # GARIS RUTE MENGIKUTI JALAN
    # ==========================================================
    # Untuk setiap pasangan titik pada rute optimal,
    # program meminta jalur jalan ke OSRM.
    # Jika internet/OSRM gagal, fallback ke garis lurus.
    # ==========================================================

    semua_koordinat_jalan = []

    for i in range(len(route_indexes) - 1):
        index_awal = route_indexes[i]
        index_tujuan = route_indexes[i + 1]

        titik_awal_segmen = koordinat[index_awal]
        titik_tujuan_segmen = koordinat[index_tujuan]

        try:
            rute_jalan = ambil_rute_jalan_osrm(
                titik_awal_segmen,
                titik_tujuan_segmen
            )

            # Hindari koordinat dobel di sambungan antarsegmen
            if semua_koordinat_jalan:
                semua_koordinat_jalan.extend(rute_jalan[1:])
            else:
                semua_koordinat_jalan.extend(rute_jalan)

        except Exception as error:
            print(
                f"OSRM gagal untuk segmen "
                f"{lokasi[index_awal]} -> {lokasi[index_tujuan]}. "
                f"Menggunakan garis lurus. Detail: {error}"
            )

            if semua_koordinat_jalan:
                semua_koordinat_jalan.append(titik_tujuan_segmen)
            else:
                semua_koordinat_jalan.extend([
                    titik_awal_segmen,
                    titik_tujuan_segmen
                ])

    folium.PolyLine(
        locations=semua_koordinat_jalan,
        color="#2563eb",
        weight=5,
        opacity=0.85,
        tooltip="Rute optimal mengikuti jalan"
    ).add_to(peta)

    # Tambahkan keterangan kecil
    legenda_html = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        font-family: Arial, sans-serif;
        font-size: 13px;
    ">
        <b>Keterangan:</b><br>
        Angka menunjukkan urutan kunjungan rute.<br>
        Label <b>1/7</b> berarti titik awal sekaligus titik akhir.
    </div>
    """

    peta.get_root().html.add_child(folium.Element(legenda_html))

    peta.save(nama_file)

    if buka_browser:
        webbrowser.open(nama_file)

    return nama_file