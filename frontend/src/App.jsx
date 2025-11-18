import React from "react";
import Sidebar from "./components/Sidebar";
import MapView from "./components/MapView";
import Toolbar from "./components/Toolbar";

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
            </div>
        </div>
    );
}
