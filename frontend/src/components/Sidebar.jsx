import { useWellsStore } from "../state/wells";

export default function Sidebar() {
  const wells = useWellsStore(state => state.wells ?? []);
  const removeWell = useWellsStore(state => state.removeWell);

  return (
    <div style={{ padding: "20px", width: "250px", height: "100%", background: "#fafafa" }}>
      <h3>Wells</h3>

      {wells.length === 0 && <p>No wells created yet.</p>}

      {wells.map(w => (
        <div
          key={w.id}
          style={{
            padding: "8px",
            marginBottom: "8px",
            border: "1px solid #ddd",
            borderRadius: "5px",
            background: "white"
          }}
        >
          <strong>{w.type === "pumping" ? "Pumping Well" : "Observation Well"}</strong>
          <br />
          Lat: {w.lat.toFixed(5)} <br />
          Lng: {w.lng.toFixed(5)}
          <br />
          <button onClick={() => removeWell(w.id)} style={{ marginTop: "5px" }}>
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}
