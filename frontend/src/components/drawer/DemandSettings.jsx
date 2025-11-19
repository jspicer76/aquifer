import { useUIStore } from "../../state/ui";
import { useState } from "react";
import { useDemandStore } from "../../state/demand";

export default function DemandSettings() {
  const close = useUIStore(s => s.closeDrawer);
  const demand = useDemandStore(s => s.demand);
  const update = useDemandStore(s => s.updateDemand);

  const [population, setPopulation] = useState(demand.population ?? 2500);
  const [gpcd, setGPCD] = useState(demand.gpcd ?? 100);
  const [curve, setCurve] = useState(
    demand.curve ??
      [1.2, 1.1, 1.05, 1.0, 0.9, 0.8, 0.85, 1.1, 1.4, 1.3, 1.2, 1.1, 1.0]
  );

  const save = () => {
    update({
      population,
      gpcd,
      curve
    });
    close();
  };

  return (
    <div style={drawerStyle}>
      <h2>Demand Settings</h2>

      <label>Population</label>
      <input value={population} onChange={e => setPopulation(Number(e.target.value))} />

      <label>GPCD</label>
      <input value={gpcd} onChange={e => setGPCD(Number(e.target.value))} />

      <label>24-hr Diurnal Curve (multiplier list)</label>
      <textarea
        value={curve.join(",")}
        onChange={e =>
          setCurve(e.target.value.split(",").map(Number))
        }
      />

      <button onClick={save}>Save</button>
      <button onClick={close}>Cancel</button>
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
