import React from "react";
import Sidebar from "./components/Sidebar";
import MapView from "./components/MapView";
import Toolbar from "./components/Toolbar";
import RightDrawer from "./components/RightDrawer";
import DrawerHost from "./components/drawers/DrawerHost";
import { useUIStore } from "../../state/ui";
import PumpingWellEditor from "./PumpingWellEditor";
import ObservationWellEditor from "./ObservationWellEditor";
import AquiferSettings from "./AquiferSettings";
import DemandSettings from "./DemandSettings";
import ResultsDrawer from "./ResultsDrawer";

export default function DrawerHost() {
  const open = useUIStore(s => s.drawerOpen);
  const type = useUIStore(s => s.drawerType);

  if (!open) return null;

  switch (type) {
    case "pumping":
      return <PumpingWellEditor />;
    case "observation":
      return <ObservationWellEditor />;
    case "aquifer":
      return <AquiferSettings />;
    case "demand":
      return <DemandSettings />;
    case "results":
      return <ResultsDrawer />;
    default:
      return null;
  }
}


export default function App() {
    return (
        <div style={{ display: "flex", height: "100vh" }}>
            <Sidebar />

            <div style={{ flex: 1, position: "relative" }}>
                <Toolbar />
                <MapView />
                <RightDrawer />   {/* <-- Add this */}
            </div>
        </div>
    );
}

{drawer.type === "results" && (
  <ResultsDrawerTabs results={drawer.payload.results} />
)}


export default function App() {
    return (
        <div style={{ display: "flex", height: "100vh" }}>
            {/* LEFT SIDEBAR */}
            <div style={{
                width: "260px",
                borderRight: "1px solid #ddd",
                padding: "10px",
                overflowY: "auto"
            }}>
                <Sidebar />
            </div>

            {/* MAIN PANEL */}
            <div style={{ flex: 1, position: "relative" }}>
                {/* Toolbar */}
                <div style={{
                    position: "absolute",
                    top: 10,
                    left: "50%",
                    transform: "translateX(-50%)",
                    zIndex: 9999,
                    background: "white",
                    padding: "8px",
                    borderRadius: "6px",
                    boxShadow: "0px 2px 6px rgba(0,0,0,0.2)"
                }}>
                    <Toolbar />
                </div>

                {/* Map */}
                <MapView />
                <DrawerHost />
            </div>
        </div>
    );
}
