import React from "react";

/**
 * WHPTab.jsx
 *
 * Displays Wellhead Protection Zones (WHP I, II, III)
 * calculated by backend:
 *
 * results.whp = {
 *   zone1_radius_ft,
 *   zone2_radius_ft,
 *   zone3_radius_ft,
 *   dh_used,
 *   plots: {
 *     whp_map: "data:image/png;base64,...",
 *     whp_capture: "base64 capture zone figure"
 *   }
 * }
 */

export default function WHPTab({ results }) {
  if (!results || !results.whp) {
    return <p>No WHP results available.</p>;
  }

  const whp = results.whp;
  const plots = whp.plots || {};

  return (
    <div style={{ paddingBottom: "40px" }}>
      <h2>Wellhead Protection Zones</h2>
      <p>
        These zones are computed using KDOW and Ten States criteria for wellhead
        protection planning. Zones are based on simulated groundwater velocities,
        porosity (Sy), pumping rate, and local gradient <em>(dh/dl)</em>.
      </p>

      {/* ---- SUMMARY GRID ---- */}
      <div style={gridStyle}>
        <MetricCard
          title="Zone I Radius"
          value={`${fmt(whp.zone1_radius_ft)} ft`}
          note="Regulated immediate protection area (KDOW)."
          highlight="good"
        />

        <MetricCard
          title="Zone II Radius"
          value={`${fmt(whp.zone2_radius_ft)} ft`}
          note="Approx. 5-year time-of-travel capture zone."
        />

        <MetricCard
          title="Zone III Radius"
          value={`${fmt(whp.zone3_radius_ft)} ft`}
          note="Regional contributing area or recharge zone."
        />

        <MetricCard
          title="Hydraulic Gradient Used"
          value={fmt(whp.dh_used)}
          note="Based on FEM drawdown + regional gradient."
        />
      </div>

      {/* ---- WHP MAP OVERLAY ---- */}
      <Section title="Wellhead Protection Map (Overlaid Zones)">
        <ImageOrPlaceholder src={plots.whp_map} />
        <p style={noteStyle}>
          WHP boundaries are superimposed on the groundwater surface elevation
          map. Zone I is typically 100 ft radius; Zone II is capture-based; Zone III
          includes the broader watershed contributing to recharge.
        </p>
      </Section>

      {/* ---- CAPTURE ZONE FIGURE ---- */}
      <Section title="Capture Zone Geometry">
        <ImageOrPlaceholder src={plots.whp_capture} />
        <p style={noteStyle}>
          Capture zone pathways show streamline trajectories converging on the
          pumping well, computed from velocity field estimates:
          <br />
          <code>v = (T / Sy) * (dh/dl)</code>
        </p>
      </Section>

      {/* ---- KDOW REQUIREMENTS ---- */}
      <Section title="Regulatory Basis (KDOW + Ten States)">
        <p style={regText}>
          <strong>KDOW Requirements:</strong>
          <ul>
            <li>Zone I must be a controlled sanitary setback (min 100 ft).</li>
            <li>
              Zone II must reflect calculated groundwater capture for a 5-year
              time-of-travel (TOT).
            </li>
            <li>
              Zone III must encompass the contributing watershed area for long-term
              recharge.
            </li>
            <li>
              Capture zone modeling should consider seasonal recharge, pumping rate,
              storage coefficient, and transmissivity.
            </li>
          </ul>

          <strong>Ten State Standards:</strong>
          <ul>
            <li>
              Section 4.2 recommends delineation of capture zones using analytical or
              numerical methods.
            </li>
            <li>
              Encourages use of regional gradient & pumping-induced gradients.
            </li>
            <li>
              Requires identification of potential contaminant sources in all zones.
            </li>
          </ul>
        </p>
      </Section>
    </div>
  );
}

/* ----------------------------
   Section Component
---------------------------- */
function Section({ title, children }) {
  return (
    <div style={{ marginTop: "35px" }}>
      <h3 style={{ marginBottom: "10px" }}>{title}</h3>
      {children}
    </div>
  );
}

/* ----------------------------
   Image/Placeholder Component
---------------------------- */
function ImageOrPlaceholder({ src }) {
  if (!src) {
    return (
      <div style={placeholderStyle}>
        <em>No WHP map available.</em>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt="WHP Zone Plot"
      style={{
        width: "100%",
        maxHeight: "450px",
        objectFit: "contain",
        borderRadius: "6px",
        border: "1px solid #ccc",
        background: "white"
      }}
    />
  );
}

/* ----------------------------
   Metric Card Component
---------------------------- */
function MetricCard({ title, value, note, highlight }) {
  return (
    <div
      style={{
        ...metricCardStyle,
        borderLeft:
          highlight === "good"
            ? "5px solid #2ba84a"
            : "5px solid #0077cc"
      }}
    >
      <div style={metricTitle}>{title}</div>
      <div style={metricValue}>{value}</div>
      <div style={metricNote}>{note}</div>
    </div>
  );
}

/* ----------------------------
   Helpers + Styles
---------------------------- */

const fmt = (v, digits = 2) =>
  typeof v === "number" ? v.toFixed(digits) : String(v);

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
  gap: "15px",
  marginTop: "20px"
};

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

const placeholderStyle = {
  height: "260px",
  width: "100%",
  borderRadius: "6px",
  border: "1px solid #ccc",
  background: "#efefef",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  color: "#777"
};

const noteStyle = {
  marginTop: "8px",
  color: "#555",
  fontSize: "12px"
};

const regText = {
  fontSize: "14px",
  color: "#333",
  lineHeight: "1.4"
};
