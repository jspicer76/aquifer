import { useUIStore } from "../../state/ui";
import { useState } from "react";
import { useAquiferStore } from "../../state/aquifer";

export default function AquiferSettings() {
  const close = useUIStore(s => s.closeDrawer);
  const aquifer = useAquiferStore(s => s.aquifer);
  const update = useAquiferStore(s => s.updateAquifer);

  const [b, setB] = useState(aquifer.b ?? 50);
  const [precip, setPrecip] = useState(aquifer.annual_precip_in ?? 46);
  const [inf, setInf] = useState(aquifer.infiltration_fraction ?? 0.25);

  const save = () => {
    update({
      b,
      annual_precip_in: precip,
      infiltration_fraction: inf
    });
    close();
  };

  return (
    <div style={drawerStyle}>
      <h2>Aquifer Properties</h2>

      <label>Saturated thickness b (ft)</label>
      <input value={b} onChange={e => setB(Number(e.target.value))} />

      <label>Annual precip (in)</label>
      <input value={precip} onChange={e => setPrecip(Number(e.target.value))} />

      <label>Infiltration fraction</label>
      <input value={inf} onChange={e => setInf(Number(e.target.value))} />

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
