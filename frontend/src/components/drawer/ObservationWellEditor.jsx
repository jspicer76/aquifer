import { useWellsStore } from "../../state/wells";
import { useUIStore } from "../../state/ui";
import { useState } from "react";

export default function ObservationWellEditor() {
  const wellId = useUIStore(s => s.drawerWellId);
  const closeDrawer = useUIStore(s => s.closeDrawer);
  const well = useWellsStore(s => s.wells[wellId]);
  const updateWell = useWellsStore(s => s.updateWellData);

  const [times, setTimes] = useState(well.data.times ?? [1, 2, 5, 10, 20]);
  const [drawdowns, setDrawdowns] = useState(
    well.data.drawdowns ?? [0.1, 0.2, 0.4, 0.6, 0.8]
  );

  const save = () => {
    updateWell(wellId, {
      times,
      drawdowns
    });
    closeDrawer();
  };

  return (
    <div style={drawerStyle}>
      <h2>Observation Well Settings</h2>

      <label>Times (min)</label>
      <textarea
        value={times.join(",")}
        onChange={e => setTimes(e.target.value.split(",").map(Number))}
      />

      <label>Drawdown (ft)</label>
      <textarea
        value={drawdowns.join(",")}
        onChange={e => setDrawdowns(e.target.value.split(",").map(Number))}
      />

      <button onClick={save}>Save</button>
      <button onClick={closeDrawer}>Cancel</button>
    </div>
  );
}

const drawerStyle = {
  padding: "20px",
  width: "350px",
  position: "fixed",
  right: 0,
  top: 0,
  bottom: 0,
  background: "white",
  boxShadow: "0 0 10px rgba(0,0,0,0.3)",
  zIndex: 99999
};
