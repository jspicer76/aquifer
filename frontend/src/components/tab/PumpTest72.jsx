import React from "react";

/**
 * PumpTest72Tab.jsx
 *
 * Displays results from the backend 72-hour pump test simulator:
 *  - drawdown curve
 *  - recovery curve
 *  - max drawdown
 *  - pass/fail against stability criteria
 *  - recommended pumping rate (safe yield)
 *  - base64 charts
 *
 * results.pump72 MUST contain:
 *  {
 *     max_drawdown_ft,
 *     final_recovery_ft,
 *     stable,
 *     recommended_yield_gpm,
 *     plots: {
 *        pump72_drawdown: "data:image/png;base64,...",
 *        pump72_recovery: "data:image/png;base64,..."
 *     }
 *  }
 */

export default function PumpTest72Tab({ results }) {
  if (!results || !results.pump72) {
    return <p>No 72-hour pump test results available.</p>;
  }

  const p = results.pump72;
  const plots = p.plots || {};

  return (
    <div style={{ paddingBottom: "40px" }}>
      <h2>72-Hour Pump Test</h2>
      <p>
        Results from the regulatory 72-hour sustained pump test simulation.  
        This stability analysis is required by KDOW and recommended in the Ten States Standards.
      </p>

      {/* --- METRICS GRID --- */}
      <div style={gridStyle}>
        <MetricCard
          title="Max Drawdown"
          value={`${fmt(p.max_drawdown_ft)} ft`}
          note="Maximum simulated drawdown at pumping well during 72 hrs."
        />

        <MetricCard
          title="Recovery After Shutoff"
          value={`${fmt(p.final_recovery_ft)} ft`}
          note="Residual drawdown after cessation of pumping."
        />

        <MetricCard
          title="Stability (72 hr)"
          value={p.stable ? "Stable ✔" : "Unstable ✖"}
          highlight={p.stable ? "good" : "bad"}
          note="Stable = < 10% change in drawdown over final 12 hours."
        />

        <MetricCard
          title="Recommended Safe Yield"
          value={`${fmt(p.recommended_yield_gpm)} gpm`}
          note="Based on drawdown stability and allowable drawdown limits."
        />
      </div>

      {/* --- WARNING IF NOT STABLE --- */}
      {!p.stable && (
        <div style={warningBox}>
          <strong>Warning:</strong>  
          The aquifer did <u>not</u> stabilize during the final portion of the 72-hr test.  
          KDOW may require reduced pumping rate or additional test data.
        </div>
      )}

      {/* ---- DRAWNDOWN PLOT ---- */}
      <Section title="72-Hour Drawdown Curve">
        <ImageOrPlaceholder src={plots.pump72_drawdown} />
        <p style={noteStyle}>
          Drawdown should flatten during later hours if the aquifer is capable of sustained yield.
          Continued decline indicates boundary effects or insufficient transmissivity.
        </p>
      </Section>

      {/* ---- RECOVERY ---- */}
      <Section title="Recovery Curve (Post-Shutoff)">
        <ImageOrPlaceholder src={plots.pump72_recovery} />
        <p style={noteStyle}>
          Rapid recovery and a small residual drawdown indicate a resilient aquifer with good hydraulic communication.
        </p>
      </Section>

      {/* ---- DUTY CYCLE SUMMARY ---- */}
      <Section title="Pumping Duty Cycle (Usage Pattern)">
        <p>
          The 72-hour test assumes continuous pumping at the provided rate.  
          Real-world demand varies diurnally. Using EPA residential/municipal patterns,
          the safe yield above will later feed into the <strong>Demand Modeling</strong> tab.
        </p>

        <ul>
          <li>Peak hour factor ~ 2.0 (EPA)</li>
          <li>Average daily usage = 60–100 gpcd (EPA + KDOW)</li>
          <li>System storage must support peak hour & fire flow (Ten States)</li>
        </ul>

        <p>
          This test confirms whether continuous pumping at the design rate is possible.  
          Demand cycles will be applied in a later tab.
        </p>
      </Section>
    </div>
  );
}

/* ------------------------------------------------
   Section Wrapper
------------------------------------------------ */
function Section({ title, children }) {
  return (
    <div style={{ marginTop: "35px" }}>
      <h3 style={{ marginBottom: "10px" }}>{title}</h3>
      {children}
    </div>
  );
}

/* --------------------------------------------
   Image or Placeholder
-------------------------------------------- */
function ImageOrPlaceholder({ src }) {
  if (!src) {
    return (
      <div style={placeholderStyle}>
        <em>No plot available.</em>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt="72-hour pump test plot"
      style={{
        width: "100%",
        maxHeight: "420px",
        objectFit: "contain",
        borderRadius: "6px",
        border: "1px solid #ccc",
        background: "white"
      }}
    />
  );
}

/* --------------------------------------------
   Metric Card
-------------------------------------------- */
function MetricCard({ title, value, note, highlight }) {
  return (
    <div
      style={{
        ...metricCardStyle,
        borderLeft:
          highlight === "good"
            ? "5px solid #28a745"
            : highlight === "bad"
            ? "5px solid #cc0000"
            : "5px solid #999"
      }}
    >
      <div style={metricTitle}>{title}</div>
      <div style={metricValue}>{value}</div>
      <div style={metricNote}>{note}</div>
    </div>
  );
}

/* ---- Helpers ---- */
function fmt(v, digits = 3) {
  return typeof v === "number" ? v.toFixed(digits) : String(v);
}

/* ---- Styles ---- */

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
  gap: "15px",
  marginTop: "20px"
};

const metricCardStyle = {
  background: "white",
  padding: "15px",
  borderRadius: "8px",
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
  fontSize: "12px",
  color: "#666",
  marginTop: "8px"
};

const warningBox = {
  marginTop: "20px",
  background: "#ffe8e8",
  padding: "12px",
  border: "1px solid #cc0000",
  borderRadius: "6px",
  color: "#990000"
};
