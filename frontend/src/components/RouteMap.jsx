import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";

const locationCoordinates = [
  [-1.26753, 116.82887], // Taman Bekapai
  [-1.26891, 116.82961], // Hotel Novotel Balikpapan
  [-1.26589, 116.83187], // Hotel Grand Senyiur Balikpapan
  [-1.26715, 116.83451], // SMPN 1 Balikpapan
  [-1.27013, 116.82835], // Balikpapan Plaza
  [-1.24284, 116.87654], // E-Walk Balikpapan
  [-1.27795, 116.81024], // Pantai Kemala
];

function createNumberIcon(number) {
  return L.divIcon({
    className: "route-number-marker",
    html: `<div>${number}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

export default function RouteMap({ locations, routeIndexes }) {
  const routeCoordinates =
    routeIndexes?.map((index) => locationCoordinates[index]) || [];

  const getRouteOrder = (locationIndex) => {
    if (!routeIndexes) return locationIndex + 1;

    const orderIndex = routeIndexes.findIndex((index) => index === locationIndex);
    return orderIndex === -1 ? locationIndex + 1 : orderIndex + 1;
  };

  return (
    <section className="card">
      <div className="section-title">
        <div>
          <p className="eyebrow">Visualisasi Rute</p>
          <h2>Peta Rute Pengantaran Paket di Balikpapan</h2>
        </div>
      </div>

      <div className="map-wrapper">
        <MapContainer
          center={[-1.2675, 116.8315]}
          zoom={13}
          scrollWheelZoom={false}
          className="leaflet-map"
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {locations.map((location, index) => (
            <Marker
              key={location}
              position={locationCoordinates[index]}
              icon={createNumberIcon(getRouteOrder(index))}
            >
              <Popup>
                <strong>
                  Urutan {getRouteOrder(index)}: {location}
                </strong>
              </Popup>
            </Marker>
          ))}

          {routeCoordinates.length > 0 && (
            <Polyline positions={routeCoordinates} weight={5} />
          )}
        </MapContainer>
      </div>
    </section>
  );
}