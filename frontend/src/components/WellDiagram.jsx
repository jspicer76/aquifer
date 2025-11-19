import React from "react";

// A clean engineering-style SVG well profile diagram
export default function WellDiagram({ well }) {
  if (!well || !well.data) return <p>No data for diagram.</p>;

  // Extract well parameters
  const casingDia = well.data.casing_diameter_in || 6;
  const boreDia = well.data.borehole_diameter_in || 10;
  const screenTop = well.data.screen_top_ft || 40;
  const screenBottom = well.data.screen_bottom_ft || 80;
  const totalDepth = well.data.total_depth_ft || 100;
  const pumpSetting = well.data.pump_setting_ft || 70;
  const staticWL = well.data.static_water_level_ft || 20;

  // SVG SCALE
  const W = 260;
  const H = 600;
  const scaleY = H / totalDepth;

  const y = v => v * scaleY;  // ft → px

  return (
    <svg width={W} height={H} style={{ border: "1px solid #ccc" }}>
      {/* Background */}
      <rect x={0} y={0} width={W} height={H} fill="#fdfdfd" />

      {/* Ground surface line */}
      <line x1={0} y1={y(0)} x2={W} y2={y(0)} stroke="black" strokeWidth={2} />
      <text x={10} y={y(0) + 15}>Ground Surface</text>

      {/* Static water level */}
      <line
        x1={0}
        y1={y(staticWL)}
        x2={W}
        y2={y(staticWL)}
        stroke="blue"
        strokeDasharray="4"
        strokeWidth={2}
      />
      <text x={10} y={y(staticWL) - 5} fill="blue">
        Static Water Level ({staticWL} ft)
      </text>

      {/* Borehole outline */}
      <rect
        x={(W - boreDia) / 2}
        y={y(0)}
        width={boreDia}
        height={y(totalDepth)}
        fill="#f0f0f0"
        stroke="#aaa"
      />

      {/* Casing */}
      <rect
        x={(W - casingDia) / 2}
        y={y(0)}
        width={casingDia}
        height={y(screenTop)}
        fill="#e6e6e6"
        stroke="#555"
      />

      {/* Screen */}
      <rect
        x={(W - casingDia) / 2}
        y={y(screenTop)}
        width={casingDia}
        height={y(screenBottom - screenTop)}
        fill="#cce5ff"
        stroke="#0077cc"
      />

      {/* Screen label */}
      <text x={10} y={y(screenTop)-5} fill="#0077cc">
        Screen Interval: {screenTop}–{screenBottom} ft
      </text>

      {/* Pump setting */}
      <circle
        cx={W/2}
        cy={y(pumpSetting)}
        r={8}
        fill="orange"
        stroke="black"
      />
      <text x={W/2 + 12} y={y(pumpSetting)+5}>
        Pump @ {pumpSetting} ft
      </text>

      {/* Total depth label */}
      <text x={10} y={y(totalDepth)-5}>Bottom: {totalDepth} ft</text>

    </svg>
  );
}
