import React from "react";

/**
 * WellDesignTab.jsx
 *
 * Displays:
 *  - Recommended well diameter
 *  - Required screen length
 *  - Gravel pack design
 *  - Hydrogeologic calculations (SC, screen area)
 *  - Pump selection (TDH, HP, efficiency)
 *  - Development time estimate
 *  - Cost estimate
 *  - Auto-generated SVG well diagram (PDF embedded)
 *
 * results.well_design MUST contain:
 *   {
 *     diameter_in_required,
 *     diameter_in_recommended,
 *     diameter_in_final,
 *     screen_length_ft,
 *     screen_length_range_ft,
 *     slot_size_in,
 *     SC_approx,
 *     screen_area_required_ft2,
 *     gravel: {...},
 *     development: {...},
 *     pump: {...},
 *     cost: {...}
 *   }
 */

export default function WellDesignTab({ results, diagramRef }) {
  if (!results || !results.well_design) {
    return <p>No well design results available.</p>;
  }

  const w = results.well_design;
  const gravel = w.gravel || {};
  const dev = w.development || {};
  const pump = w.pump || {};
  const cost = w.cost || {};

  return (
    <div style={{ paddingBottom: "40px" }}>
      <h2>Well Design Recommendations</h2>
      <p>
        This tab summarizes recommended well construction parameters consistent with
        KDOW, AWWA A100, and Ten States Standards.
      </p>

      {/* --- SUMMARY GRID --- */}
      <div style={gridStyle}>
        <MetricCard
          title="Recommended Diameter"
          value={`${fmt(w.diameter_in_recommended)} in`}
          note={`Required minimum was ${fmt(w.diameter_in_required)} in`}
        />

        <MetricCard
          title="Final Diameter Used"
          value={`${fmt(w.diameter_in_final)} in`}
          note="Selected based on screen area & pump installation clearance."
        />

        <MetricCard
          title="Screen Length"
          value={`${fmt(w.screen_length_ft)} ft`}
          note={`Acceptable range: ${fmt(w.screen_length_range_ft[0])}–${fmt(
            w.screen_length_range_ft[1]
          )} ft`}
        />

        <MetricCard
          title="Estimated Specific Capacity"
          value={`${fmt(w.SC_approx)} gpm/ft`}
          note="Based on transmissivity and drawdown."
        />

        <MetricCard
          title="Required Screen Area"
          value={`${fmt(w.screen_area_required_ft2)} ft²`}
          note="Based on AWWA allowable entrance velocity."
        />

        <MetricCard
          title="Slot Size"
          value={`${fmt(w.slot_size_in)} in`}
          note="Based on filter pack D10 sizing."
        />
      </div>

      {/* --- GRAVEL PACK DESIGN --- */}
      <Section title="Gravel Pack Design">
        <DesignList
          items={[
            [`Filter D10`, `${fmt(gravel.GP_D10_mm)} mm`],
            [`Filter D50`, `${fmt(gravel.GP_D50_mm)} mm`],
            [`Thickness`, `${fmt(gravel.thickness_ft)} ft`],
            [`Porosity`, `${fmt(gravel.porosity)}`],
            [`Slot Size`, `${fmt(gravel.slot_size_in)} in`]
          ]}
        />
        <p style={noteStyle}>{gravel.notes}</p>
      </Section>

      {/* --- WELL DEVELOPMENT --- */}
      <Section title="Well Development Estimate">
        <DesignList
          items={[
            ["Airlift Time", `${fmt(dev.airlift_hours)} hrs`],
            ["Jetting Time", `${fmt(dev.jetting_hours)} hrs`],
            ["Expected Range", `${fmt(dev.range_hours[0])}–${fmt(
              dev.range_hours[1]
            )} hrs`]
          ]}
        />
        <p style={noteStyle}>{dev.notes}</p>
      </Section>

      {/* --- PUMP SELECTION --- */}
      <Section title="Pump Selection & TDH Calculation">
        <DesignList
          items={[
            ["Static Lift", `${fmt(pump.static_lift_ft)} ft`],
            ["Friction Loss", `${fmt(pump.friction_loss_ft)} ft`],
            ["Total Dynamic Head", `${fmt(pump.TDH_ft)} ft`],
            ["Calculated HP", `${fmt(pump.HP_calc)} hp`],
            ["Recommended Motor", `${fmt(pump.HP_recommended)} hp`],
            ["Efficiency", `${fmt(pump.efficiency * 100)} %`]
          ]}
        />
        <p style={noteStyle}>{pump.notes}</p>
      </Section>

      {/* --- COST ESTIMATE --- */}
      <Section title="Estimated Construction Cost">
        <DesignList
          items={[
            ["Drilling", usd(cost.drilling)],
            ["Screen", usd(cost.screen_cost)],
            ["Development", usd(cost.development)],
            ["Mobilization", usd(cost.mobilization)],
            ["Total Cost", usd(cost.total_cost)]
          ]}
        />
      </Section>

      {/* --- WELL DIAGRAM --- */}
      <Section title="Well Construction Diagram">
        <p>This auto-generated diagram is included in the PDF export.</p>

        <div ref={diagramRef} style={diagramBox}>
          <WellDiagram
            diameter={w.diameter_in_final}
            screenLength={w.screen_length_ft}
            gravel={gravel}
          />
        </div>
      </Section>
    </div>
  );
}

/* ------------------------------------------------
   SVG WELL DIAGRAM
------------------------------------------------ */
function WellDiagram({ diameter, screenLength, gravel }) {
  const diagramHeight = 300;
  const screenHeight = Math.max(40, (screenLength / 50) * 60);

  return (
    <svg width="250" height={diagramHeight} style={{ background: "#fefefe" }}>
      {/* Casing */}
      <rect
        x="90"
        y="10"
        width="70"
        height={diagramHeight - 20}
        fill="#d0d0d0"
        stroke="#444"
      />

      {/* Screen area */}
      <rect
        x="95"
        y={diagramHeight - screenHeight - 20}
        width="60"
        height={screenHeight}
        fill="#f2d98d"
        stroke="#b89443"
      />

      {/* Gravel Pack */}
      <rect
        x="70"
        y={diagramHeight - screenHeight - 20}
        width="20"
        height={screenHeight}
        fill="#ccb47a"
        stroke="#8f784f"
      />

      <text x="50" y="25" fontSize="12" fill="#333">
        Diameter: {diameter} in
      </text>
      <text x="50" y="45" fontSize="12" fill="#333">
        Screen: {screenLength} ft
      </text>
      <text x="50" y="65" fontSize="12" fill="#333">
        Gravel D50: {gravel.GP_D50_mm} mm
      </text>
    </svg>
  );
}

/* ------------------------------------------------
   Reusable helpers
------------------------------------------------ */

function DesignList({ items }) {
  return (
    <table style={tableStyle}>
      <tbody>
        {items.map(([label, value], idx) => (
          <tr key={idx}>
            <td style={tdLabel}>{label}</td>
            <td style={tdValue}>{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* ------------------------------------------------
   UI helpers
------------------------------------------------ */

function fmt(v, digits = 2) {
  return typeof v === "number" ? v.toFixed(digits) : String(v);
}

function usd(v) {
  return typeof v === "number"
    ? `$${v.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
    : v;
}

/* ------------------------------------------------
   Styles
------------------------------------------------ */

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
  gap: "15px",
  marginTop: "20px"
};

function MetricCard({ title, value, note }) {
  return (
    <div style={metricCardStyle}>
      <div style={metricTitle}>{title}</div>
      <div style={metricValue}>{value}</div>
      <div style={metricNote}>{note}</div>
    </div>
  );
}

const metricCardStyle = {
  background: "white",
  borderRadius: "8px",
  padding: "15px",
  boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
  border: "1px solid #ddd"
};

const metricTitle = {
  fontSize: "14px",
  fontWeight: "bold",
  marginBottom: "6px"
};

const metricValue = {
  fontSize: "20px",
  fontWeight: "700",
  margin: "8px 0"
};

const metricNote = {
  fontSize: "12px",
  color: "#666"
};

const noteStyle = {
  fontSize: "12px",
  color: "#666",
  marginTop: "8px"
};

const sectionStyle = {};

function Section({ title, children }) {
  return (
    <div style={{ marginTop: "35px" }}>
      <h3 style={{ marginBottom: "10px" }}>{title}</h3>
      {children}
    </div>
  );
}

const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
  marginBottom: "10px"
};

const tdLabel = {
  width: "50%",
  padding: "6px",
  fontWeight: "bold",
  fontSize: "14px",
  borderBottom: "1px solid #ddd"
};

const tdValue = {
  padding: "6px",
  fontSize: "14px",
  borderBottom: "1px solid #ddd"
};

const diagramBox = {
  background: "white",
  padding: "15px",
  borderRadius: "8px",
  border: "1px solid #ccc",
  display: "flex",
  justifyContent: "center"
};
