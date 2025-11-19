import React from "react";
import { useWellsStore } from "../state/wells";
import { useUIStore } from "../state/ui";

export default function Toolbar() {
  const setMode = useWellsStore(s => s.setMode);
  const openDrawer = useUIStore(s => s.openDrawer);
  const runModel = useModelRunner(s => s.runModel);

  return (
    <div style={{ display: "flex", gap: "10px" }}>
      <button onClick={() => setMode("pumping")}>Add Pumping Well</button>
      <button onClick={() => setMode("observation")}>Add Observation Well</button>
      <button onClick={() => openDrawer("aquifer")}>Aquifer Settings</button>
      <button onClick={() => openDrawer("demand")}>System Demand</button>
      <button onClick={() => setMode(null)}>Cancel</button>
      <button onClick={() => useUIStore.getState().openDrawer("aquifer")}>
        Aquifer Settings
      </button>

      <button onClick={() => useUIStore.getState().openDrawer("demand")}>
        Demand Settings
      </button>

      <button onClick={() => runModel()}>
        Run Aquifer Model
      </button>
    </div>
  );
}


const activeButtonStyle = {
  backgroundColor: "#1976d2",
  color: "#fff"
};

export default function Toolbar() {
  const {
    addPumpingWell,
    addObservationWell,
    runModel,
    mode,
    isRunning,
    wellsCount,
    lastRunSummary,
    error
  } = useWellsStore((state) => ({
    addPumpingWell: state.addPumpingWell,
    addObservationWell: state.addObservationWell,
    runModel: state.runModel,
    mode: state.mode,
    isRunning: state.isRunning,
    wellsCount: state.wells.length,
    lastRunSummary: state.lastRunSummary,
    error: state.error
  }));

  const modelDisabled = isRunning || wellsCount === 0;
  const activeLabel = mode
    ? `Placing ${mode === "pumping" ? "Pumping" : "Observation"} Well`
    : "Select a tool";

  return (
    <div className="toolbar">
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={addPumpingWell}
          style={mode === "pumping" ? activeButtonStyle : undefined}
        >
          Add Pumping Well
        </button>
        <button
          type="button"
          onClick={addObservationWell}
          style={mode === "observation" ? activeButtonStyle : undefined}
        >
          Add Observation Well
        </button>
        <button
          type="button"
          onClick={runModel}
          disabled={modelDisabled}
        >
          {isRunning ? "Running model..." : "Run Aquifer Model"}
        </button>
      </div>

      <div style={{ marginTop: "6px", fontSize: "0.85rem" }}>
        <div>Active tool: {activeLabel}</div>
        {modelDisabled && wellsCount === 0 && (
          <div style={{ color: "#555" }}>Add at least one well to enable the model.</div>
        )}
        {lastRunSummary && (
          <div style={{ color: "#0b8043" }}>
            Last run at {new Date(lastRunSummary.timestamp).toLocaleTimeString()} &middot; Aquifer type:{" "}
            {lastRunSummary.aquifer_type ?? "n/a"}
          </div>
        )}
        {error && (
          <div style={{ color: "#b00020" }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
