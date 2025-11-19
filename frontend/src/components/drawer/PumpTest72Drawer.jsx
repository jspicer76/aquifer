import { useState } from "react";
import { Line } from "react-chartjs-2";
import { useUIStore } from "../../state/ui";

export default function PumpTest72Drawer({ results }) {
  const close = useUIStore(s => s.closeDrawer);

  if (!results || !results.pump72) return <p>No data.</p>;

  const t = results.pump72.times_hr;
  const dd = results.pump72.drawdown_ft;
  const wl = results.pump72.water_level_ft;

  return (
    <div style={drawerStyle}>
      <h2>72-Hour Sustained Pump Test</h2>

      <Line
        data={{
          labels: t,
          datasets: [
            {
              label: "Drawdown (ft)",
              data: dd,
              borderColor: "red",
              fill: false
            },
            {
              label: "Water Level (ft)",
              data: wl,
              borderColor: "blue",
              fill: false
            }
          ]
        }}
      />

      <button onClick={close} style={{ marginTop: "15px" }}>
        Close
      </button>
    </div>
  );
}

const drawerStyle = {
  padding: "20px",
  width: "500px",
  position: "fixed",
  right: 0,
  top: 0,
  bottom: 0,
  background: "white",
  overflowY: "scroll",
  boxShadow: "0 0 10px rgba(0,0,0,0.3)",
  zIndex: 99999
};
