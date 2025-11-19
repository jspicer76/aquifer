import React from "react";

/**
 * OverviewTab
 * Shows the high-level summary of aquifer results, pumping test data,
 * design recommendations, and classification.
 *
 * results = {
 *   theis: { T, S },
 *   cooper_jacob: { T, S },
 *   neuman: { T, Sy },
 *   recovery: { T },
 *   calibration: { T, Sy },
 *   recharge,
 *   well_design,
 *   classification,
 *   pump72,
 *   whp
 * }
 */

export default function OverviewTab({ results, mapRef }) {
  if (!results) return <p>No results available.</p>;

  const { theis, cooper_jacob, neuman, calibration, recharge, classification } =
    results;

  const pretty = (v, digits = 3) =>
    typeof v === "number" ? v.toFixed(digits) : String(v);

  return (
    <div style={{ paddingBottom: "40px" }}>
      <h2 style={{ marginTop: 0 }}>Overview</h2>

      {/* -------- SUMMARY GRID -------- */}
      <div style={gridStyle}>
        <SummaryCard
          title="Transmissivity (Calibrated)"
          value={`${pretty(calibration.T)} ft²/day`}
          note="Based on least-squares calibration using Theis response."
        />

        <SummaryCard
          title="Specific Yield (Calibrated)"
          value={`${pretty(calibration.Sy)}`}
          note="Estimated from Neuman delayed-yield model."
        />

        <SummaryCard
          title="Storativity (Theis)"
          value={`${pretty(theis.S, 2)}`}
          note="Classic Theis curve-fit storativity."
        />

        <SummaryCard
          title="Recharge"
          value={`${pretty(recharge)} gpd/acre`}
          note="Annual recharge = precip × infiltration coefficient."
        />

        <SummaryCard
          title="Aquifer Type"
          value={classification.type}
          note={classification.reason}
        />

        <SummaryCard
          title="Pumping Test"
          value={`${pretty(results.Q_gpm)} gpm`}
          note="User-provided withdrawal during pumping test."
        />
      </div>

      {/* -------- MAP SNAPSHOT AREA -------- */}
      <h3 style={{ marginTop: "40px" }}>Map Overview</h3>
      <p>
        This is a placeholder. When exporting the PDF, the app will capture a
        live snapshot of the map showing pumping/observation wells and contours.
      </p>

      <div
        ref={mapRef}
        style={{
          height: "250px",
          width: "100%",
          background: "#eaeaea",
          borderRadius: "8px",
          border: "1px solid #ccc",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontStyle: "italic",
          color: "#666"
        }}
      >
        (Map snapshot will appear here in exported PDF)
      </div>
    </div>
  );
}

/* ---------------------------
   Shared Summary Card Component
---------------------------- */
function SummaryCard({ title, value, note }) {
  return (
    <div style={cardStyle}>
      <div style={cardTitle}>{title}</div>
      <div style={cardValue}>{value}</div>
      <div style={cardNote}>{note}</div>
    </div>
  );
}

/* ----------- STYLES ----------- */

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
  gap: "15px",
  marginTop: "15px"
};

const cardStyle = {
  background: "white",
  borderRadius: "8px",
  padding: "15px",
  boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
  border: "1px solid #ddd"
};

const cardTitle = {
  fontSize: "14px",
  fontWeight: "bold",
  marginBottom: "6px"
};

const cardValue = {
  fontSize: "20px",
  fontWeight: "700",
  margin: "8px 0"
};

const cardNote = {
  fontSize: "12px",
  color: "#666"
};
