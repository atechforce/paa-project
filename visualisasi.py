# visualisasi.py
# Membuat visualisasi rute TSP pada peta HTML menggunakan Folium.
# Mendukung perbandingan dua algoritma (DP vs Brute Force) dengan dropdown.
# Garis rute dibuat mengikuti jalan menggunakan OSRM jika internet tersedia.
# Jika OSRM gagal, program otomatis memakai garis lurus sebagai cadangan.

import json
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


def _bangun_koordinat_jalan(route_indexes):
    """
    Helper: Bangun daftar koordinat jalan untuk suatu rute
    menggunakan OSRM. Fallback ke garis lurus jika OSRM gagal.
    """
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

    return semua_koordinat_jalan


def _bangun_data_marker(route_indexes):
    """
    Helper: Bangun data marker urutan untuk suatu rute.
    Mengembalikan list of dict dengan lat, lon, label, nama.
    """
    marker_urutan = {}

    for urutan, index_lokasi in enumerate(route_indexes, start=1):
        if index_lokasi not in marker_urutan:
            marker_urutan[index_lokasi] = [urutan]
        else:
            marker_urutan[index_lokasi].append(urutan)

    data_markers = []
    for index_lokasi, daftar_urutan in marker_urutan.items():
        nama_lokasi = lokasi[index_lokasi]
        lat, lon = koordinat[index_lokasi]
        label = "/".join(map(str, daftar_urutan))

        data_markers.append({
            "lat": lat,
            "lon": lon,
            "label": label,
            "nama": nama_lokasi,
        })

    return data_markers


def _bangun_data_waypoints(route_indexes):
    """Helper: Bangun data waypoint untuk animasi."""
    waypoints = []
    for idx in route_indexes:
        lat, lon = koordinat[idx]
        waypoints.append({
            "lat": lat,
            "lon": lon,
            "nama": lokasi[idx]
        })
    return waypoints


def _tambah_dropdown_dan_rute(peta, data_dp, data_bf):
    """
    Inject JavaScript dan CSS untuk:
    - Menggambar polyline dan marker untuk kedua algoritma
    - Dropdown untuk memilih algoritma
    - Animasi marker bergerak yang mengikuti rute terpilih
    """

    dropdown_js = f"""
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

        #algo-dropdown-container {{
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 9999;
            background: white;
            padding: 14px 18px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            font-family: Arial, sans-serif;
            font-size: 13px;
            min-width: 240px;
        }}

        #algo-dropdown-container select {{
            width: 100%;
            padding: 8px 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            background: white;
            transition: border-color 0.2s;
        }}

        #algo-dropdown-container select:focus {{
            outline: none;
            border-color: #2563eb;
        }}

        #algo-info {{
            margin-top: 8px;
            font-size: 12px;
            color: #6b7280;
            line-height: 1.5;
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

        .marker-dp div {{
            background-color: #2563eb !important;
        }}

        .marker-bf div {{
            background-color: #10b981 !important;
        }}
    </style>

    <!-- Dropdown pemilih algoritma -->
    <div id="algo-dropdown-container">
        <b>📊 Pilih Algoritma</b>
        <select id="algo-select" onchange="switchAlgorithm(this.value)">
            <option value="dp">🔵 Dynamic Programming</option>
            <option value="bf">🟢 Brute Force</option>
        </select>
        <div id="algo-info">
            Jarak: <b id="info-jarak">-</b> km |
            Waktu: <b id="info-waktu">-</b> detik
        </div>
    </div>

    <!-- Kontrol animasi -->
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

        // === DATA ===
        var dataDP = {json.dumps(data_dp)};
        var dataBF = {json.dumps(data_bf)};

        var mapObj = null;
        for (var key in window) {{
            if (window[key] instanceof L.Map) {{
                mapObj = window[key];
                break;
            }}
        }}

        if (!mapObj) {{
            console.error("Peta Leaflet tidak ditemukan.");
            return;
        }}

        // === BUAT MARKER ICON ===
        function buatMarkerIcon(label, color) {{
            return L.divIcon({{
                html: '<div style="' +
                    'background-color:' + color + ';' +
                    'color:white;' +
                    'min-width:34px;' +
                    'height:34px;' +
                    'padding:0 6px;' +
                    'border-radius:999px;' +
                    'text-align:center;' +
                    'line-height:34px;' +
                    'font-weight:bold;' +
                    'border:3px solid white;' +
                    'box-shadow:0 2px 8px rgba(0,0,0,0.35);' +
                    'font-size:13px;' +
                    'font-family:Arial,sans-serif;' +
                    '">' + label + '</div>',
                className: 'empty',
                iconSize: [34, 34],
                iconAnchor: [17, 17]
            }});
        }}

        // === BUAT LAYER GROUP ===
        function buatLayerGroup(data, color) {{
            var group = L.layerGroup();

            // Polyline
            if (data.koordinat_jalan.length > 0) {{
                L.polyline(data.koordinat_jalan, {{
                    color: color,
                    weight: 5,
                    opacity: 0.85
                }}).addTo(group);
            }}

            // Marker urutan
            for (var i = 0; i < data.markers.length; i++) {{
                var m = data.markers[i];
                L.marker([m.lat, m.lon], {{
                    icon: buatMarkerIcon(m.label, color),
                    zIndexOffset: 600
                }}).bindPopup("Urutan " + m.label + ": " + m.nama)
                  .bindTooltip("Urutan " + m.label + ": " + m.nama, {{sticky: true}})
                  .addTo(group);
            }}

            return group;
        }}

        var dpColor = "#2563eb";
        var bfColor = "#10b981";

        var groupDP = buatLayerGroup(dataDP, dpColor);
        var groupBF = buatLayerGroup(dataBF, bfColor);

        // Tampilkan DP secara default
        groupDP.addTo(mapObj);

        var currentAlgo = "dp";

        // Update info
        function updateInfo(algo) {{
            var data = (algo === "dp") ? dataDP : dataBF;
            document.getElementById('info-jarak').textContent = data.jarak.toFixed(2);
            document.getElementById('info-waktu').textContent = data.waktu.toFixed(8);
        }}
        updateInfo("dp");

        // === SWITCH ALGORITMA ===
        window.switchAlgorithm = function(algo) {{
            // Stop animasi jika sedang berjalan
            pauseAnimasi();
            resetAnimasi();

            if (algo === "dp") {{
                mapObj.removeLayer(groupBF);
                groupDP.addTo(mapObj);
            }} else {{
                mapObj.removeLayer(groupDP);
                groupBF.addTo(mapObj);
            }}

            currentAlgo = algo;
            updateInfo(algo);
        }};

        // === ANIMASI ===
        var animasiMarker = null;
        var trailMarkers = [];
        var currentIndex = 0;
        var isPlaying = false;
        var animasiInterval = null;
        var MAX_TRAIL = 25;

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

        function getRuteAktif() {{
            return (currentAlgo === "dp") ? dataDP.koordinat_jalan : dataBF.koordinat_jalan;
        }}

        function getWaypointsAktif() {{
            return (currentAlgo === "dp") ? dataDP.waypoints : dataBF.waypoints;
        }}

        // Inisialisasi marker animasi
        var ruteAwal = getRuteAktif();
        if (ruteAwal.length > 0) {{
            animasiMarker = L.marker(ruteAwal[0], {{
                icon: animasiIcon,
                zIndexOffset: 1000
            }}).addTo(mapObj);
        }}

        function getSpeed() {{
            var slider = document.getElementById('speed-slider');
            var val = parseInt(slider.value);
            return Math.max(10, 120 - (val * 12));
        }}

        function cekWaypoint(lat, lon) {{
            var wps = getWaypointsAktif();
            for (var i = 0; i < wps.length; i++) {{
                var wp = wps[i];
                var dist = Math.sqrt(
                    Math.pow(lat - wp.lat, 2) + Math.pow(lon - wp.lon, 2)
                );
                if (dist < 0.0003) return wp.nama;
            }}
            return null;
        }}

        function updateProgress() {{
            var rute = getRuteAktif();
            var persen = (currentIndex / (rute.length - 1)) * 100;
            document.getElementById('animasi-progress-fill').style.width = persen + '%';
        }}

        function tambahTrail(latlng) {{
            var trail = L.marker(latlng, {{
                icon: trailIcon,
                interactive: false,
                zIndexOffset: 500
            }}).addTo(mapObj);

            trailMarkers.push(trail);

            if (trailMarkers.length > MAX_TRAIL) {{
                var old = trailMarkers.shift();
                mapObj.removeLayer(old);
            }}
        }}

        function langkahAnimasi() {{
            var rute = getRuteAktif();

            if (currentIndex >= rute.length - 1) {{
                pauseAnimasi();
                document.getElementById('animasi-info').innerHTML =
                    '✅ Selesai! Kurir kembali ke titik awal.';
                document.getElementById('btn-play').innerHTML = '▶ Play';
                document.getElementById('animasi-progress-fill').style.width = '100%';
                return;
            }}

            currentIndex++;
            var pos = rute[currentIndex];
            animasiMarker.setLatLng(pos);

            if (currentIndex % 3 === 0) {{
                tambahTrail(pos);
            }}

            updateProgress();

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

        function resetAnimasi() {{
            currentIndex = 0;
            var rute = getRuteAktif();
            if (rute.length > 0 && animasiMarker) {{
                animasiMarker.setLatLng(rute[0]);
            }}
            hapusTrail();
            updateProgress();
            document.getElementById('btn-play').innerHTML = '▶ Play';
            document.getElementById('animasi-info').innerHTML = 'Tekan Play untuk mulai';
        }}

        window.toggleAnimasi = function() {{
            if (isPlaying) {{
                pauseAnimasi();
                document.getElementById('btn-play').innerHTML = '▶ Play';
                document.getElementById('animasi-info').innerHTML = '⏸ Dijeda';
            }} else {{
                var rute = getRuteAktif();
                if (currentIndex >= rute.length - 1) {{
                    resetAnimasi();
                }}
                startAnimasi();
                document.getElementById('btn-play').innerHTML = '⏸ Pause';
                document.getElementById('animasi-info').innerHTML = '🚗 Sedang berjalan...';
            }}
        }};

        window.restartAnimasi = function() {{
            pauseAnimasi();
            resetAnimasi();
        }};

    }});
    </script>
    """

    peta.get_root().html.add_child(folium.Element(dropdown_js))


def buat_peta_rute(hasil_dp, hasil_bf=None, nama_file="peta_rute_tsp.html", buka_browser=False):
    """
    Membuat file HTML berisi peta rute optimal.
    Mendukung perbandingan dua algoritma jika hasil_bf diberikan.

    Parameter:
    hasil_dp:
        dictionary hasil dari solve_tsp_dp()
        harus memiliki key "route_indexes"

    hasil_bf:
        dictionary hasil dari solve_tsp_bf() (opsional)
        jika diberikan, peta akan memiliki dropdown untuk memilih algoritma

    nama_file:
        nama file HTML output

    buka_browser:
        jika True, file HTML langsung dibuka di browser
    """

    route_indexes_dp = hasil_dp["route_indexes"]

    if not route_indexes_dp:
        raise ValueError("Route indexes kosong. Tidak dapat membuat peta.")

    titik_awal = koordinat[route_indexes_dp[0]]

    peta = folium.Map(
        location=titik_awal,
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    # ==========================================================
    # BANGUN KOORDINAT JALAN UNTUK DP
    # ==========================================================

    print("Membangun rute jalan untuk Dynamic Programming...")
    koordinat_jalan_dp = _bangun_koordinat_jalan(route_indexes_dp)
    markers_dp = _bangun_data_marker(route_indexes_dp)
    waypoints_dp = _bangun_data_waypoints(route_indexes_dp)

    data_dp = {
        "koordinat_jalan": koordinat_jalan_dp,
        "markers": markers_dp,
        "waypoints": waypoints_dp,
        "jarak": hasil_dp["minimum_distance"],
        "waktu": hasil_dp["execution_time"],
    }

    # ==========================================================
    # BANGUN KOORDINAT JALAN UNTUK BF (jika ada)
    # ==========================================================

    if hasil_bf is not None:
        route_indexes_bf = hasil_bf["route_indexes"]

        # Cek apakah rute BF sama dengan DP untuk menghindari
        # pemanggilan OSRM yang duplikat.
        if route_indexes_bf == route_indexes_dp:
            print("Rute Brute Force sama dengan DP, menggunakan koordinat yang sama.")
            koordinat_jalan_bf = koordinat_jalan_dp
        else:
            print("Membangun rute jalan untuk Brute Force...")
            koordinat_jalan_bf = _bangun_koordinat_jalan(route_indexes_bf)

        markers_bf = _bangun_data_marker(route_indexes_bf)
        waypoints_bf = _bangun_data_waypoints(route_indexes_bf)

        data_bf = {
            "koordinat_jalan": koordinat_jalan_bf,
            "markers": markers_bf,
            "waypoints": waypoints_bf,
            "jarak": hasil_bf["minimum_distance"],
            "waktu": hasil_bf["execution_time"],
        }

        # Gunakan dropdown + dual route
        _tambah_dropdown_dan_rute(peta, data_dp, data_bf)

    else:
        # Mode single algorithm (backward compatible)
        # Gambar marker urutan
        for m in markers_dp:
            folium.Marker(
                location=[m["lat"], m["lon"]],
                popup=f"Urutan {m['label']}: {m['nama']}",
                tooltip=f"Urutan {m['label']}: {m['nama']}",
                icon=buat_marker_angka(m["label"])
            ).add_to(peta)

        # Gambar polyline
        folium.PolyLine(
            locations=koordinat_jalan_dp,
            color="#2563eb",
            weight=5,
            opacity=0.85,
            tooltip="Rute optimal mengikuti jalan"
        ).add_to(peta)

        # Animasi single route
        tambah_animasi_rute(peta, koordinat_jalan_dp, route_indexes_dp)

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


def tambah_animasi_rute(peta, semua_koordinat_jalan, route_indexes):
    """
    Menambahkan animasi marker bergerak pada peta Folium.
    (Digunakan hanya untuk mode single algorithm / backward compatible)

    Marker berupa titik merah berpulsa yang bergerak mengikuti
    seluruh koordinat rute dari titik awal hingga kembali ke titik awal.
    Termasuk tombol kontrol Play/Pause/Restart dan efek trail.

    Parameter:
    peta                : objek folium.Map
    semua_koordinat_jalan: list of (lat, lon) koordinat jalur rute lengkap
    route_indexes       : list of int, urutan index lokasi pada rute
    """

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