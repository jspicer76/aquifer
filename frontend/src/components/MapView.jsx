import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { useWellsStore } from "../state/wells";

// Custom icons
const pumpingIcon = new L.Icon({
  iconUrl: "/icons/pumpwell.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32]
});

const observationIcon = new L.Icon({
  iconUrl: "/icons/obswell.png",
  iconSize: [28, 28],
  iconAnchor: [14, 28]
});

// This now reads global mode from Zustand (NOT props)
function MapClickHandler() {
  const mode = useWellsStore(s => s.mode);
  const addWell = useWellsStore(s => s.addWell);

  useMapEvents({
    click(e) {
      if (!mode) return;

      const { lat, lng } = e.latlng;
      addWell(mode, lat, lng);
    }
  });

  return null;
}

export default function MapView() {
  const wells = useWellsStore(s => s.wells);

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <MapContainer
        center={[38.30, -85.95]}
        zoom={12}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='Map data © OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Click handler listens for map clicks */}
        <MapClickHandler />

        {/* Render wells */}
        {Object.values(wells).map(well => (
          <Marker
            key={well.id}
            position={[well.lat, well.lng]}
            icon={well.type === "pumping" ? pumpingIcon : observationIcon}
          >
            <Popup>
              <strong>
                {well.type === "pumping" ? "Pumping Well" : "Observation Well"}
              </strong>
              <br />
              Lat: {well.lat.toFixed(5)} <br />
              Lng: {well.lng.toFixed(5)}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
