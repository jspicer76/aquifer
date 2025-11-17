import { useWellsStore } from "../state/wells";

export default function WellPropertiesPanel({ selectedWellId }) {
    const well = useWellsStore(state => state.wells[selectedWellId]);
    const updateWellData = useWellsStore(state => state.updateWellData);

    if (!well) return null;

    function updateField(field, value) {
        updateWellData(well.id, { [field]: value });
    }

    return (
        <div className="panel">
            <h3>{well.type === "pumping" ? "Pumping Well" : "Observation Well"}</h3>

            <label>Pumping Rate (gpm)</label>
            <input 
                type="number" 
                value={well.data.Q_gpm || ""} 
                onChange={e => updateField("Q_gpm", Number(e.target.value))}
            />

            <label>Drawdown (comma-separated)</label>
            <textarea
                value={well.data.drawdown || ""}
                onChange={e => updateField("drawdown", e.target.value)}
            />

            <label>Time (comma-separated minutes)</label>
            <textarea
                value={well.data.time || ""}
                onChange={e => updateField("time", e.target.value)}
            />

            <label>Static Water Level (ft)</label>
            <input
                type="number"
                value={well.data.static_level_ft || ""}
                onChange={e => updateField("static_level_ft", Number(e.target.value))}
            />

            <label>Depth (ft)</label>
            <input
                type="number"
                value={well.data.depth_ft || ""}
                onChange={e => updateField("depth_ft", Number(e.target.value))}
            />

            <button onClick={() => useWellsStore.getState().removeWell(well.id)}>
                Delete Well
            </button>
        </div>
    );
}
