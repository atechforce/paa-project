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


def tambah_animasi_rute(peta, semua_koordinat_jalan, route_indexes):
    """
    Menambahkan animasi marker bergerak pada peta Folium.

    Marker berupa titik merah berpulsa yang bergerak mengikuti
    seluruh koordinat rute dari titik awal hingga kembali ke titik awal.
    Termasuk tombol kontrol Play/Pause/Restart dan efek trail.

    Parameter:
    peta                : objek folium.Map
    semua_koordinat_jalan: list of (lat, lon) koordinat jalur rute lengkap
    route_indexes       : list of int, urutan index lokasi pada rute
    """

    import json

    koordinat_json = json.dumps(semua_koordinat_jalan)

    # Kumpulkan index koordinat yang merupakan titik lokasi (waypoint)
    # agar animasi bisa menampilkan nama lokasi saat melewati titik tersebut.
    waypoint_coords = []
    for idx in route_indexes:
        lat, lon = koordinat[idx]
        waypoint_coords.append({
            "lat": lat,
            "lon": lon,
            "nama": lokasi[idx]
        })

    waypoint_json = json.dumps(waypoint_coords)

    animasi_js = f"""
    <style>
        @keyframes pulse-ring {{
            0%   {{ transform: scale(0.5); opacity: 1; }}
            100% {{ transform: scale(2.5); opacity: 0; }}
        }}

        .animasi-marker {{
            width: 18px;
            height: 18px;
            background: #ef4444;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 12px 4px rgba(239,68,68,0.5);
            position: relative;
        }}

        .animasi-marker::before {{
            content: '';
            position: absolute;
            top: -4px;
            left: -4px;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: rgba(239,68,68,0.4);
            animation: pulse-ring 1.2s ease-out infinite;
        }}

        .animasi-trail {{
            width: 8px;
            height: 8px;
            background: rgba(239,68,68,0.5);
            border-radius: 50%;
            pointer-events: none;
        }}

        #animasi-kontrol {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 9999;
            background: white;
            padding: 12px 16px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            font-family: Arial, sans-serif;
            font-size: 13px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 200px;
        }}

        #animasi-kontrol button {{
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            transition: all 0.2s ease;
        }}

        #btn-play {{
            background: #2563eb;
            color: white;
        }}
        #btn-play:hover {{
            background: #1d4ed8;
        }}

        #btn-restart {{
            background: #f3f4f6;
            color: #374151;
        }}
        #btn-restart:hover {{
            background: #e5e7eb;
        }}

        #animasi-info {{
            font-size: 12px;
            color: #6b7280;
            text-align: center;
            min-height: 18px;
        }}

        #animasi-progress-bar {{
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
        }}

        #animasi-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #ef4444);
            border-radius: 3px;
            width: 0%;
            transition: width 0.1s linear;
        }}

        #speed-kontrol {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #6b7280;
        }}

        #speed-kontrol input {{
            flex: 1;
        }}
    </style>

    <div id="animasi-kontrol">
        <b>🚗 Animasi Rute</b>
        <div id="animasi-progress-bar">
            <div id="animasi-progress-fill"></div>
        </div>
        <div id="animasi-info">Tekan Play untuk mulai</div>
        <div id="speed-kontrol">
            <span>Lambat</span>
            <input type="range" id="speed-slider" min="1" max="10" value="5">
            <span>Cepat</span>
        </div>
        <div style="display:flex; gap:8px;">
            <button id="btn-play" onclick="toggleAnimasi()">▶ Play</button>
            <button id="btn-restart" onclick="restartAnimasi()">↻ Restart</button>
        </div>
    </div>

    <script>
    window.addEventListener('load', function() {{
        var ruteKoordinat = {koordinat_json};
        var waypoints = {waypoint_json};

        var mapObj = null;
        // Cari objek peta Leaflet yang sudah dibuat oleh Folium
        for (var key in window) {{
            if (window[key] instanceof L.Map) {{
                mapObj = window[key];
                break;
            }}
        }}

        if (!mapObj) {{
            console.error("Objek peta Leaflet tidak ditemukan.");
            return;
        }}

        var animasiMarker = null;
        var trailMarkers = [];
        var currentIndex = 0;
        var isPlaying = false;
        var animasiInterval = null;
        var MAX_TRAIL = 25;

        // Buat icon animasi
        var animasiIcon = L.divIcon({{
            html: '<div class="animasi-marker"></div>',
            className: 'animasi-marker-container',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        }});

        var trailIcon = L.divIcon({{
            html: '<div class="animasi-trail"></div>',
            className: '',
            iconSize: [8, 8],
            iconAnchor: [4, 4]
        }});

        // Inisialisasi marker di titik awal
        if (ruteKoordinat.length > 0) {{
            animasiMarker = L.marker(ruteKoordinat[0], {{
                icon: animasiIcon,
                zIndexOffset: 1000
            }}).addTo(mapObj);
        }}

        function getSpeed() {{
            var slider = document.getElementById('speed-slider');
            var val = parseInt(slider.value);
            // Semakin besar slider, semakin cepat (interval lebih kecil)
            return Math.max(10, 120 - (val * 12));
        }}

        function cekWaypoint(lat, lon) {{
            for (var i = 0; i < waypoints.length; i++) {{
                var wp = waypoints[i];
                var dist = Math.sqrt(
                    Math.pow(lat - wp.lat, 2) + Math.pow(lon - wp.lon, 2)
                );
                if (dist < 0.0003) {{
                    return wp.nama;
                }}
            }}
            return null;
        }}

        function updateProgress() {{
            var persen = (currentIndex / (ruteKoordinat.length - 1)) * 100;
            document.getElementById('animasi-progress-fill').style.width = persen + '%';
        }}

        function tambahTrail(latlng) {{
            var trail = L.marker(latlng, {{
                icon: trailIcon,
                interactive: false,
                zIndexOffset: 500
            }}).addTo(mapObj);

            trailMarkers.push(trail);

            // Batasi jumlah trail agar tidak berat
            if (trailMarkers.length > MAX_TRAIL) {{
                var old = trailMarkers.shift();
                mapObj.removeLayer(old);
            }}
        }}

        function langkahAnimasi() {{
            if (currentIndex >= ruteKoordinat.length - 1) {{
                // Animasi selesai
                pauseAnimasi();
                document.getElementById('animasi-info').innerHTML =
                    '✅ Selesai! Kurir kembali ke titik awal.';
                document.getElementById('btn-play').innerHTML = '▶ Play';
                document.getElementById('animasi-progress-fill').style.width = '100%';
                return;
            }}

            currentIndex++;
            var pos = ruteKoordinat[currentIndex];
            animasiMarker.setLatLng(pos);

            // Tambah trail setiap beberapa langkah
            if (currentIndex % 3 === 0) {{
                tambahTrail(pos);
            }}

            updateProgress();

            // Cek apakah sampai di waypoint
            var namaLokasi = cekWaypoint(pos[0], pos[1]);
            if (namaLokasi) {{
                document.getElementById('animasi-info').innerHTML =
                    '📍 Melewati: <b>' + namaLokasi + '</b>';
            }}
        }}

        function startAnimasi() {{
            if (isPlaying) return;
            isPlaying = true;

            animasiInterval = setInterval(function() {{
                langkahAnimasi();
            }}, getSpeed());

            // Update speed secara dinamis
            document.getElementById('speed-slider').addEventListener('input', function() {{
                if (isPlaying) {{
                    clearInterval(animasiInterval);
                    animasiInterval = setInterval(function() {{
                        langkahAnimasi();
                    }}, getSpeed());
                }}
            }});
        }}

        function pauseAnimasi() {{
            isPlaying = false;
            if (animasiInterval) {{
                clearInterval(animasiInterval);
                animasiInterval = null;
            }}
        }}

        function hapusTrail() {{
            for (var i = 0; i < trailMarkers.length; i++) {{
                mapObj.removeLayer(trailMarkers[i]);
            }}
            trailMarkers = [];
        }}

        // Fungsi global untuk tombol
        window.toggleAnimasi = function() {{
            if (isPlaying) {{
                pauseAnimasi();
                document.getElementById('btn-play').innerHTML = '▶ Play';
                document.getElementById('animasi-info').innerHTML = '⏸ Dijeda';
            }} else {{
                // Jika sudah selesai, restart dulu
                if (currentIndex >= ruteKoordinat.length - 1) {{
                    currentIndex = 0;
                    animasiMarker.setLatLng(ruteKoordinat[0]);
                    hapusTrail();
                    updateProgress();
                }}

                startAnimasi();
                document.getElementById('btn-play').innerHTML = '⏸ Pause';
                document.getElementById('animasi-info').innerHTML = '🚗 Sedang berjalan...';
            }}
        }};

        window.restartAnimasi = function() {{
            pauseAnimasi();
            currentIndex = 0;
            animasiMarker.setLatLng(ruteKoordinat[0]);
            hapusTrail();
            updateProgress();
            document.getElementById('btn-play').innerHTML = '▶ Play';
            document.getElementById('animasi-info').innerHTML = 'Tekan Play untuk mulai';
        }};
    }});
    </script>
    """

    peta.get_root().html.add_child(folium.Element(animasi_js))


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

    # ==========================================================
    # ANIMASI MARKER BERGERAK
    # ==========================================================
    # Menambahkan animasi titik merah berpulsa yang bergerak
    # mengikuti seluruh koordinat rute dari awal hingga kembali.
    # ==========================================================

    tambah_animasi_rute(peta, semua_koordinat_jalan, route_indexes)

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