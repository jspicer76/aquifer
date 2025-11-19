import Sidebar from "./components/Sidebar";
import MapView from "./components/MapView";
import Toolbar from "./components/Toolbar";
import RightDrawer from "./components/RightDrawer";

export default function App() {
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "#f5f7fb"
      }}
    >
      <div
        style={{
          width: 280,
          borderRight: "1px solid #e1e4e8",
          background: "#ffffff",
          padding: "12px 10px",
          overflowY: "auto"
        }}
      >
        <Sidebar />
      </div>

      <div style={{ flex: 1, position: "relative" }}>
        <div
          style={{
            position: "absolute",
            top: 12,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 1000,
            pointerEvents: "none"
          }}
        >
          <div style={{ pointerEvents: "auto" }}>
            <Toolbar />
          </div>
        </div>

        <MapView />
        <RightDrawer />
      </div>
    </div>
  );
}
