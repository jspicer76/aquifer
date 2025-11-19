import { MapContainer, TileLayer, Marker, Popup, Polyline, Polygon } from "react-leaflet";
import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet-draw";
import { useWellsStore } from "../state/wells";
import { useBoundaryStore } from "../state/boundaries";
import BoundaryMetadataModal from "./BoundaryMetadataModal";


// Icons
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

export default function MapView() {
  const wells = useWellsStore(s => Object.values(s.wells));
  const boundaryStore = useBoundaryStore();

  const mapRef = useRef(null);
  const drawnItems = useRef(null);

  const [metadataMode, setMetadataMode] = useState(null);
  const [pendingGeometry, setPendingGeometry] = useState([]);
  const [pendingBoundary, setPendingBoundary] = useState(null);

  const styles = {
    chb: { color: "#003f91", weight: 3 },
    noflow: { color: "#c1121f", weight: 3 },
    recharge: { color: "#2a9d8f", weight: 2, fillColor: "#2a9d8f", fillOpacity: 0.3 },
    ghb: { color: "#f77f00", weight: 3, dashArray: "6,6" }
  };

  // ---------------------------------------------------------
  // INITIALIZE MAP + DRAW HANDLERS
  // ---------------------------------------------------------
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    drawnItems.current = new L.FeatureGroup();
    map.addLayer(drawnItems.current);

    let drawControl = null;

    // Subscribe to boundary store draw mode
    const unsub = useBoundaryStore.subscribe((state) => {
      if (drawControl) map.removeControl(drawControl);

      if (state.editMode) {
        drawControl = new L.Control.Draw({
          draw: false,
          edit: { featureGroup: drawnItems.current }
        });
        map.addControl(drawControl);
        return;
      }

      if (!state.drawMode) return;

      let mode = state.drawMode;
      let drawOptions = {
        draw: {
          polyline: false,
          polygon: false,
          rectangle: false,
          marker: false,
          circle: false,
          circlemarker: false
        },
        edit: false
      };

      if (mode === "chb") drawOptions.draw.polyline = { shapeOptions: styles.chb };
      if (mode === "noflow") drawOptions.draw.polyline = { shapeOptions: styles.noflow };
      if (mode === "ghb") drawOptions.draw.polyline = { shapeOptions: styles.ghb };
      if (mode === "recharge") drawOptions.draw.polygon = { shapeOptions: styles.recharge };

      drawControl = new L.Control.Draw(drawOptions);
      map.addControl(drawControl);
    });

    // Handle DRAW COMPLETE
    map.on(L.Draw.Event.CREATED, function (e) {
      const layer = e.layer;
      drawnItems.current.addLayer(layer);

      const mode = useBoundaryStore.getState().drawMode;
      if (!mode) return;

      // Convert leaflet geometry
      let coords = [];
      if (layer.getLatLngs) {
        const ll = layer.getLatLngs();
        if (Array.isArray(ll[0])) coords = ll[0].map((pt) => [pt.lat, pt.lng]);
        else coords = ll.map((pt) => [pt.lat, pt.lng]);
      }

      // Save geometry temporarily until metadata entered
      setPendingGeometry(coords);
      setPendingBoundary(null);
      setMetadataMode(mode);

      // Stop drawing
      useBoundaryStore.getState().stopDraw();
    });

    // Handle EDIT COMPLETE
    map.on("draw:edited", function (e) {
      e.layers.eachLayer((layer) => {
        const id = layer.options.boundaryId;
        const type = layer.options.boundaryType;

        if (!id || !type) return;

        let ll = layer.getLatLngs();
        let coords = Array.isArray(ll[0])
          ? ll[0].map((pt) => [pt.lat, pt.lng])
          : ll.map((pt) => [pt.lat, pt.lng]);

        useBoundaryStore.getState().updateGeometry(type, id, coords);
      });
    });

    return () => unsub();
  }, []);

  // ---------------------------------------------------------
  // SUBMIT METADATA FROM MODAL
  // ---------------------------------------------------------
  function handleMetadataSubmit(meta) {
    if (!metadataMode) return;

    if (pendingBoundary) {
      boundaryStore.updateMetadata(pendingBoundary.type, pendingBoundary.id, meta);
    } else {
      boundaryStore.addBoundary(metadataMode, pendingGeometry, meta);
    }

    setMetadataMode(null);
    setPendingGeometry([]);
    setPendingBoundary(null);
  }

  function handleDelete() {
    if (pendingBoundary) {
      boundaryStore.removeBoundary(pendingBoundary.type, pendingBoundary.id);
    }
    setMetadataMode(null);
    setPendingBoundary(null);
    setPendingGeometry([]);
  }

  function handleEditGeometry() {
    if (pendingBoundary) {
      boundaryStore.startEdit();
    }
    setMetadataMode(null);
    setPendingBoundary(null);
  }

  function handleClose() {
    setMetadataMode(null);
    setPendingGeometry([]);
    setPendingBoundary(null);
  }

  const currentBoundary =
    pendingBoundary && boundaryStore[pendingBoundary.type]
      ? boundaryStore[pendingBoundary.type].find((b) => b.id === pendingBoundary.id)
      : null;

  // ---------------------------------------------------------
  // RENDER
  // ---------------------------------------------------------
  return (
    <div style={{ width: "100%", height: "100%" }}>
      <MapContainer
        center={[38.3, -85.9]}
        zoom={12}
        style={{ width: "100%", height: "100%" }}
        whenCreated={map => (mapRef.current = map)}
      >
        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Wells */}
        {wells.map((w) => (
          <Marker
            key={w.id}
            position={[w.lat, w.lng]}
            icon={w.type === "pumping" ? pumpingIcon : observationIcon}
          >
            <Popup>
              <strong>{w.type === "pumping" ? "Pumping Well" : "Observation Well"}</strong>
              <br />
              Lat: {w.lat.toFixed(5)} <br />
              Lng: {w.lng.toFixed(5)}
            </Popup>
          </Marker>
        ))}

        {/* CLICKABLE BOUNDARIES */}
        {boundaryStore.constantHead.map(b => (
          <Polyline
            key={b.id}
            positions={b.points}
            pathOptions={styles.chb}
            eventHandlers={{
              click: () => {
                setMetadataMode("chb");
                setPendingBoundary({ type: "constantHead", id: b.id });
                setPendingGeometry([]);
              }
            }}
          />
        ))}

        {boundaryStore.noFlow.map(b => (
          <Polyline
            key={b.id}
            positions={b.points}
            pathOptions={styles.noflow}
            eventHandlers={{
              click: () => {
                setMetadataMode("noflow");
                setPendingBoundary({ type: "noFlow", id: b.id });
                setPendingGeometry([]);
              }
            }}
          />
        ))}

        {boundaryStore.rechargeZones.map(b => (
          <Polygon
            key={b.id}
            positions={b.polygon}
            pathOptions={styles.recharge}
            eventHandlers={{
              click: () => {
                setMetadataMode("recharge");
                setPendingBoundary({ type: "rechargeZones", id: b.id });
                setPendingGeometry([]);
              }
            }}
          />
        ))}

        {boundaryStore.generalHead.map(b => (
          <Polyline
            key={b.id}
            positions={b.points}
            pathOptions={styles.ghb}
            eventHandlers={{
              click: () => {
                setMetadataMode("ghb");
                setPendingBoundary({ type: "generalHead", id: b.id });
                setPendingGeometry([]);
              }
            }}
          />
        ))}

      </MapContainer>

      <BoundaryMetadataModal
        open={metadataMode !== null}
        mode={metadataMode}
        selected={currentBoundary}
        onClose={handleClose}
        onSubmit={handleMetadataSubmit}
        onDelete={pendingBoundary ? handleDelete : undefined}
        onEditGeometry={pendingBoundary ? handleEditGeometry : undefined}
      />
    </div>
  );
}
