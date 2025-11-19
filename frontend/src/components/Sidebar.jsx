import { useState } from "react";
import { useWellsStore } from "../state/wells";
import { useBoundariesStore } from "../state/boundaries";

export default function Sidebar() {
  const wells = useWellsStore(s => Object.values(s.wells));
  const removeWell = useWellsStore(s => s.removeWell);

  const boundaries = useBoundariesStore(s => s);
  const [activeTab, setActiveTab] = useState("wells");

  return (
    <div style={{ padding: "15px", width: "260px", overflowY: "auto" }}>
      {/* TAB SELECTOR */}
      <div style={{ display: "flex", gap: "6px", marginBottom: "10px" }}>
        <button onClick={() => setActiveTab("wells")}>Wells</button>
        <button onClick={() => setActiveTab("boundaries")}>Boundaries</button>
        <button onClick={() => setActiveTab("inputs")}>Inputs</button>
      </div>

      {/* -----------------------------
          TAB: WELLS
      ------------------------------ */}
      {activeTab === "wells" && (
        <>
          <h3>Wells</h3>
          {wells.length === 0 && <p>No wells yet.</p>}
          {wells.map(w => (
            <div key={w.id} style={boxStyle}>
              <strong>{w.type === "pumping" ? "Pumping Well" : "Observation Well"}</strong>
              <br />
              Lat: {w.lat.toFixed(5)} <br />
              Lng: {w.lng.toFixed(5)} <br/>

              <button style={{ marginTop:"6px" }} onClick={() => removeWell(w.id)}>
                Remove
              </button>
            </div>
          ))}
        </>
      )}

      {/* -----------------------------
          TAB: BOUNDARIES
      ------------------------------ */}
      {activeTab === "boundaries" && (
        <>
          <h3>Boundary Conditions</h3>
          <p>Select a boundary type below and draw on the map.</p>

          {/* CONSTANT HEAD */}
          <div style={boxStyle}>
            <strong>Constant-Head Boundary (Rivers)</strong><br/>
            <button onClick={() => boundaries.startDraw("chb")}>
              Draw CHB Polyline
            </button>
            <button onClick={() => boundaries.stopDraw()}>Stop</button>

            {boundaries.constantHead.length > 0 && (
              <ul>
                {boundaries.constantHead.map((b, idx) => (
                  <li key={idx}>CHB #{idx+1}</li>
                ))}
              </ul>
            )}
          </div>

          {/* NO-FLOW */}
          <div style={boxStyle}>
            <strong>No-Flow Boundary</strong><br/>
            <button onClick={() => boundaries.startDraw("noflow")}>
              Draw No-Flow Line
            </button>
            <button onClick={() => boundaries.stopDraw()}>Stop</button>

            {boundaries.noFlow.length > 0 && (
              <ul>
                {boundaries.noFlow.map((b, idx) => (
                  <li key={idx}>No-Flow #{idx+1}</li>
                ))}
              </ul>
            )}
          </div>

          {/* RECHARGE ZONE */}
          <div style={boxStyle}>
            <strong>Recharge Zone (Polygon)</strong><br/>
            <button onClick={() => boundaries.startDraw("recharge")}>
              Draw Recharge Polygon
            </button>
            <button onClick={() => boundaries.stopDraw()}>Stop</button>

            {boundaries.rechargeZones.length > 0 && (
              <ul>
                {boundaries.rechargeZones.map((b, idx) => (
                  <li key={idx}>Recharge Zone #{idx+1}</li>
                ))}
              </ul>
            )}
          </div>

          {/* GENERAL-HEAD */}
          <div style={boxStyle}>
            <strong>General-Head Boundary</strong><br/>
            <button onClick={() => boundaries.startDraw("ghb")}>
              Draw GHB Polyline
            </button>
            <button onClick={() => boundaries.stopDraw()}>Stop</button>

            {boundaries.generalHead.length > 0 && (
              <ul>
                {boundaries.generalHead.map((b, idx) => (
                  <li key={idx}>GHB #{idx+1}</li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}

      {/* -----------------------------
          TAB: INPUTS (AQUIFER / PUMP)
      ------------------------------ */}
      {activeTab === "inputs" && (
        <>
          <h3>Model Inputs</h3>
          <p>Here we will add full pumping-test input tables, aquifer parameters, recharge, well design overrides, etc.</p>
        </>
      )}
    </div>
  );
}

const boxStyle = {
  padding: "8px",
  border: "1px solid #ddd",
  borderRadius: "5px",
  background: "white",
  marginBottom: "10px"
};
