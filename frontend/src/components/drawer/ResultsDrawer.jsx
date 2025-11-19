import { useState, useRef } from "react";
import { useUIStore } from "../../state/ui";
import { useResultsStore } from "../../state/results";
import { generatePDFReport } from "../../utils/pdfReport";

import OverviewTab from "../tab/OverviewTab";
import AnalyticalTab from "../tab/AnalyticalTab";
import PumpTest72Tab from "../tab/PumpTest72";
import WHPTab from "../tab/WHPTab";
import WellDesignTab from "../tab/WellDesignTab";

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "analytical", label: "Analytical Fits" },
  { id: "pump72", label: "72-Hr Pump Test" },
  { id: "whp", label: "WHP Zones" },
  { id: "welldesign", label: "Well Design" }
];

export default function ResultsDrawer() {
  const close = useUIStore(s => s.closeDrawer);
  const results = useResultsStore(s => s.results);
  const [active, setActive] = useState("overview");
  const diagramRef = useRef(null);
  const mapRef = useRef(null);

  if (!results) return null;

  return (
    <div style={drawerStyle}>
      <div style={headerStyle}>
        <h2 style={{ margin: 0 }}>Aquifer Analysis Results</h2>
        <button type="button" onClick={close}>
          Close
        </button>
      </div>

      <div style={tabBarStyle}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            style={{
              ...tabStyle,
              ...(active === tab.id ? tabActiveStyle : {})
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div style={contentStyle}>
        {active === "overview" && (
          <OverviewTab results={results} mapRef={mapRef} />
        )}
        {active === "analytical" && <AnalyticalTab results={results} />}
        {active === "pump72" && <PumpTest72Tab results={results} />}
        {active === "whp" && <WHPTab results={results} />}
        {active === "welldesign" && (
          <WellDesignTab results={results} diagramRef={diagramRef} />
        )}
      </div>

      <div style={footerStyle}>
        <button
          type="button"
          onClick={() => generatePDFReport(results, diagramRef, mapRef)}
          style={pdfButtonStyle}
        >
          Export PDF Report
        </button>
      </div>
    </div>
  );
}

const drawerStyle = {
  position: "fixed",
  top: 0,
  right: 0,
  bottom: 0,
  width: 650,
  background: "#fff",
  boxShadow: "0 0 15px rgba(0,0,0,0.25)",
  zIndex: 10000,
  display: "flex",
  flexDirection: "column"
};

const headerStyle = {
  padding: 20,
  borderBottom: "1px solid #ddd",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center"
};

const tabBarStyle = {
  display: "flex",
  borderBottom: "1px solid #ddd",
  background: "#f5f5f5"
};

const tabStyle = {
  flex: 1,
  padding: "10px 12px",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  fontSize: 14
};

const tabActiveStyle = {
  borderBottom: "3px solid #0077cc",
  fontWeight: 600,
  background: "#fff"
};

const contentStyle = {
  flex: 1,
  overflowY: "auto",
  padding: 20
};

const footerStyle = {
  padding: 12,
  borderTop: "1px solid #ddd",
  textAlign: "center"
};

const pdfButtonStyle = {
  padding: "10px 20px",
  background: "#0077cc",
  color: "#fff",
  border: "none",
  borderRadius: 4,
  cursor: "pointer"
};
