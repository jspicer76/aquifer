import React, { useState, useRef } from "react";
import { useUIStore } from "../../state/ui";
import { generatePDFReport } from "../../utils/pdfReport";

// Components for each tab (we’ll define below)
import OverviewTab from "../tabs/OverviewTab";
import AnalyticalTab from "../tabs/AnalyticalTab";
import PumpTest72Tab from "../tabs/PumpTest72Tab";
import WHPTab from "../tabs/WHPTab";
import WellDesignTab from "../tabs/WellDesignTab";

export default function ResultsDrawerTabs({ results }) {
  const close = useUIStore(s => s.closeDrawer);

  const [active, setActive] = useState("overview");

  // Refs for PDF export (map + diagram snapshots)
  const diagramRef = useRef(null);
  const mapRef = useRef(null);

  if (!results) return null;

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "analytical", label: "Analytical Fits" },
    { id: "pump72", label: "72-Hr Pump Test" },
    { id: "whp", label: "WHP Zones" },
    { id: "welldesign", label: "Well Design" }
  ];

  return (
    <div style={drawerStyle}>
      {/* HEADER */}
      <div style={headerStyle}>
        <h2>Aquifer Analysis Results</h2>
        <button onClick={close}>✖ Close</button>
      </div>

      {/* TABS */}
      <div style={tabBarStyle}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActive(t.id)}
            style={{
              ...tabStyle,
              ...(active === t.id ? tabActiveStyle : {})
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}
      <div style={contentStyle}>
        {active === "overview" && (
          <OverviewTab results={results} mapRef={mapRef} />
        )}
        {active === "analytical" && (
          <AnalyticalTab results={results} />
        )}
        {active === "pump72" && (
          <PumpTest72Tab results={results} />
        )}
        {active === "whp" && (
          <WHPTab results={results} />
        )}
        {active === "welldesign" && (
          <WellDesignTab results={results} diagramRef={diagramRef} />
        )}
      </div>

      {/* FOOTER — PDF EXPORT */}
      <div style={footerStyle}>
        <button
          onClick={() => generatePDFReport(results, diagramRef, mapRef)}
          style={pdfButtonStyle}
        >
          📄 Export PDF Report
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
  width: "650px",
  background: "white",
  boxShadow: "0 0 15px rgba(0,0,0,0.25)",
  zIndex: 99999,
  display: "flex",
  flexDirection: "column"
};

const headerStyle = {
  padding: "20px",
  borderBottom: "1px solid #ddd",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center"
};

const tabBarStyle = {
  display: "flex",
  borderBottom: "1px solid #ddd",
  background: "#f8f8f8"
};

const tabStyle = {
  flex: 1,
  padding: "10px",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  fontSize: "14px"
};

const tabActiveStyle = {
  borderBottom: "3px solid #0077cc",
  fontWeight: "bold",
  background: "white"
};

const contentStyle = {
  flex: 1,
  overflowY: "auto",
  padding: "20px"
};

const footerStyle = {
  padding: "10px",
  borderTop: "1px solid #ddd",
  textAlign: "center"
};

const pdfButtonStyle = {
  padding: "10px 20px",
  background: "#0077cc",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer"
};
