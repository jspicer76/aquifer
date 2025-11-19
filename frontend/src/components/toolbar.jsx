import { useWellsStore } from "../state/wells";
import { useUIStore } from "../state/ui";

const buttonStyle = {
  padding: "8px 12px",
  borderRadius: 4,
  border: "1px solid #d0d7de",
  background: "#fff",
  cursor: "pointer"
};

const activeButton = {
  ...buttonStyle,
  background: "#0d6efd",
  color: "#fff",
  borderColor: "#0d6efd"
};

export default function Toolbar() {
  const addPumpingWell = useWellsStore(s => s.addPumpingWell);
  const addObservationWell = useWellsStore(s => s.addObservationWell);
  const clearMode = useWellsStore(s => s.clearMode);
  const runModel = useWellsStore(s => s.runModel);
  const mode = useWellsStore(s => s.mode);
  const isRunning = useWellsStore(s => s.isRunning);
  const wellsCount = useWellsStore(s => s.wells.length);
  const lastRunSummary = useWellsStore(s => s.lastRunSummary);
  const error = useWellsStore(s => s.error);
  const openDrawer = useUIStore(s => s.openDrawer);

  const disableRun = isRunning || wellsCount === 0;
  const placementLabel = mode
    ? `Placing ${mode === "pumping" ? "pumping" : "observation"} well`
    : "Select a tool to begin";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
        padding: "10px 14px",
        background: "#fff",
        borderRadius: 10,
        boxShadow: "0 4px 15px rgba(15,23,42,0.12)"
      }}
    >
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={addPumpingWell}
          style={mode === "pumping" ? activeButton : buttonStyle}
        >
          Add Pumping Well
        </button>
        <button
          type="button"
          onClick={addObservationWell}
          style={mode === "observation" ? activeButton : buttonStyle}
        >
          Add Observation Well
        </button>
        <button type="button" onClick={clearMode} style={buttonStyle}>
          Cancel Placement
        </button>
        <button
          type="button"
          onClick={() => openDrawer("aquifer")}
          style={buttonStyle}
        >
          Aquifer Settings
        </button>
        <button
          type="button"
          onClick={() => openDrawer("demand")}
          style={buttonStyle}
        >
          System Demand
        </button>
        <button
          type="button"
          onClick={runModel}
          disabled={disableRun}
          style={{
            ...buttonStyle,
            background: disableRun ? "#f0f0f0" : "#198754",
            color: disableRun ? "#777" : "#fff",
            borderColor: disableRun ? "#d0d0d0" : "#198754",
            cursor: disableRun ? "not-allowed" : "pointer"
          }}
        >
          {isRunning ? "Running..." : "Run Aquifer Model"}
        </button>
      </div>

      <div style={{ fontSize: 13, color: "#0f172a" }}>
        <div>{placementLabel}</div>
        {disableRun && wellsCount === 0 && (
          <div style={{ color: "#6c757d" }}>
            Add at least one well to enable the simulation.
          </div>
        )}
        {lastRunSummary && (
          <div style={{ color: "#0d9488" }}>
            Last run at{" "}
            {new Date(lastRunSummary.timestamp).toLocaleTimeString()} – Aquifer{" "}
            {lastRunSummary.aquifer_type ?? "n/a"}
          </div>
        )}
        {error && (
          <div style={{ color: "#b91c1c" }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
