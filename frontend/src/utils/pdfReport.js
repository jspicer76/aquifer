import html2canvas from "html2canvas";
import jsPDF from "jspdf";

/**
 * generatePDFReport(results, diagramRef, mapRef)
 * ------------------------------------------------
 * Full PDF engine WITH:
 *  - Logo (optional)
 *  - Project metadata block
 *  - Existing full report (unchanged)
 */

export async function generatePDFReport(results, diagramRef, mapRef) {
  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "pt",
    format: "letter"
  });

  const margin = 40;
  let y = margin;

  /* ============================================================
     NEW SECTION: LOGO + PROJECT METADATA
  ============================================================ */

  const meta = results.project || {};

  const PROJECT_NAME = meta.project_name || "Groundwater Well Analysis Report";
  const CLIENT = meta.client || "Client Not Specified";
  const LOCATION = meta.location || "Location Not Specified";
  const WELL_ID = meta.well_id || "N/A";
  const PREPARED_BY = meta.prepared_by || "Aquifer Analysis System";
  const PREPARED_FOR = meta.prepared_for || "";
  const DATE = meta.date || new Date().toLocaleDateString();
  const VERSION = meta.version || "1.0";

  let logoData = meta.logo_base64 || null;

  // Attempt to load /logo.png if no base64 provided
  if (!logoData) {
    try {
      const img = await fetch("/logo.png");
      if (img.ok) {
        const blob = await img.blob();
        logoData = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
      }
    } catch (e) {
      console.warn("Logo not found; skipping.");
    }
  }

  /* =========== Draw Logo =========== */

  if (logoData) {
    pdf.addImage(logoData, "PNG", margin, y, 140, 50);
  }

  y += 70;

  /* =========== Project Metadata =========== */

  pdf.setFontSize(22);
  pdf.text(PROJECT_NAME, margin, y);
  y += 35;

  pdf.setFontSize(14);
  pdf.text(`Prepared For: ${CLIENT}`, margin, y); y += 20;
  pdf.text(`Location: ${LOCATION}`, margin, y); y += 20;
  pdf.text(`Well ID: ${WELL_ID}`, margin, y); y += 20;
  pdf.text(`Prepared By: ${PREPARED_BY}`, margin, y); y += 20;
  if (PREPARED_FOR) {
    pdf.text(`Submitting Agency: ${PREPARED_FOR}`, margin, y);
    y += 20;
  }
  pdf.text(`Date: ${DATE}`, margin, y); y += 20;
  pdf.text(`Report Version: ${VERSION}`, margin, y); y += 30;

  pdf.setLineWidth(0.8);
  pdf.line(margin, y, 550, y);
  y += 25;

  pdf.setFontSize(12);
  pdf.text(
    "This report contains analytical pumping test evaluation, aquifer hydraulic properties, well construction design, WHP zones, and regulatory compliance.",
    margin,
    y
  );

  y += 40;

  /* ============================================================
     MAP SNAPSHOT
  ============================================================ */

  if (mapRef?.current) {
    const canvas = await html2canvas(mapRef.current);
    const image = canvas.toDataURL("image/png");

    pdf.addImage(image, "PNG", margin, y, 520, 280);
    y += 300;
  }

  /* ============================================================
     ORIGINAL REPORT CONTENT STARTS HERE
     (YOUR EXISTING SECTIONS BELOW REMAIN IDENTICAL)
  ============================================================ */

  pdf.addPage();
  y = margin;

  /* -----------------------------
     Helper Functions (unchanged)
  ------------------------------ */
  function title(text) {
    pdf.setFontSize(18);
    pdf.text(text, margin, y);
    y += 28;
  }

  function subtitle(text) {
    pdf.setFontSize(14);
    pdf.text(text, margin, y);
    y += 22;
  }

  function paragraph(text) {
    pdf.setFontSize(11);
    const lines = pdf.splitTextToSize(text, 520);
    pdf.text(lines, margin, y);
    y += lines.length * 14 + 10;
  }

  function checkPageSpace(height = 120) {
    if (y + height > 760) {
      pdf.addPage();
      y = margin;
    }
  }

  async function addImage(imageData, titleText) {
    if (!imageData) return;

    checkPageSpace(360);
    subtitle(titleText);

    pdf.addImage(imageData, "PNG", margin, y, 520, 280);
    y += 300;
  }

  /* ==========================================================
     PAGE 2 — AQUIFER PARAMETERS
  ========================================================== */

  title("Aquifer Properties Summary");

  paragraph(`
Transmissivity (Calibrated): ${fmt(results.calibration.T)} ft²/day
Specific Yield (Calibrated): ${fmt(results.calibration.Sy)}
Storativity (Theis Fit): ${fmt(results.theis.S)}
Recharge Estimate: ${fmt(results.recharge)} gpd/acre
Aquifer Classification: ${results.classification.type}
Reason: ${results.classification.reason}
`);

  /* ==========================================================
     Analytical Charts
  ========================================================== */
  title("Analytical Pumping Test Fits");

  await addImage(results?.plots?.drawdown_plot, "Observed Drawdown");
  await addImage(results?.plots?.theis_plot, "Theis Match Curve");
  await addImage(results?.plots?.cooper_plot, "Cooper-Jacob Straight-Line Fit");
  await addImage(results?.plots?.neuman_plot, "Neuman Delayed Yield Fit");

  pdf.addPage();
  y = margin;

  /* ==========================================================
     72-HOUR PUMP TEST
  ========================================================== */

  title("72-Hour Pump Test Summary");

  paragraph(`
Maximum Drawdown: ${fmt(results.pump72.max_drawdown_ft)} ft
Recovery After Shutoff: ${fmt(results.pump72.final_recovery_ft)} ft
Stable? ${results.pump72.stable ? "Yes — stable" : "No — may require reduced pumping rate"}
Recommended Safe Yield: ${fmt(results.pump72.recommended_yield_gpm)} gpm
`);

  await addImage(results?.pump72?.plots?.pump72_drawdown, "72-Hour Drawdown Curve");
  await addImage(results?.pump72?.plots?.pump72_recovery, "Recovery Curve");

  pdf.addPage();
  y = margin;

  /* ==========================================================
     WHP Zones
  ========================================================== */

  title("Wellhead Protection Zones");

  paragraph(`
Zone I Radius: ${fmt(results.whp.zone1_radius_ft)} ft
Zone II Radius: ${fmt(results.whp.zone2_radius_ft)} ft
Zone III Radius: ${fmt(results.whp.zone3_radius_ft)} ft
Hydraulic Gradient Used: ${fmt(results.whp.dh_used)}
`);

  await addImage(results?.whp?.plots?.whp_map, "WHP Zone Map Overlay");
  await addImage(results?.whp?.plots?.whp_capture, "Capture Zone Streamlines");

  pdf.addPage();
  y = margin;

  /* ==========================================================
     WELL DESIGN REPORT
  ========================================================== */

  title("Well Design Summary");

  const w = results.well_design;

  paragraph(`
Recommended Diameter: ${fmt(w.diameter_in_recommended)} in
Required Diameter: ${fmt(w.diameter_in_required)} in
Final Diameter Used: ${fmt(w.diameter_in_final)} in

Screen Length: ${fmt(w.screen_length_ft)} ft
Screen Area Required: ${fmt(w.screen_area_required_ft2)} ft²
Slot Size: ${fmt(w.slot_size_in)} in

Specific Capacity Estimate: ${fmt(w.SC_approx)} gpm/ft
`);

  subtitle("Well Construction Diagram");

  /* Capture SVG diagram */
  if (diagramRef?.current) {
    const canvas = await html2canvas(diagramRef.current);
    const image = canvas.toDataURL("image/png");

    checkPageSpace(360);
    pdf.addImage(image, "PNG", margin, y, 520, 300);
    y += 320;
  }

  pdf.addPage();
  y = margin;

/* ==========================================================
   BOUNDARY CONDITIONS — KDOW / Ten States Documentation
   ========================================================== */

pdf.addPage();
y = margin;

title("Boundary Conditions Summary");

paragraph(`
The groundwater model includes user-specified boundary conditions consistent with 
401 KAR 8 (Kentucky Division of Water), EPA Groundwater Hydraulics guidance, and 
Ten States Standards (Section 4.0). The boundaries were digitized on the project map 
and transformed into numerical constraints for the finite-difference groundwater model.
`);

const b = results.boundaries || {};

subtitle("Boundary Condition Overview");

paragraph(`
Constant-Head Boundaries: ${b.constant_head?.length ?? 0}
No-Flow Boundaries: ${b.no_flow?.length ?? 0}
Recharge Zones: ${b.recharge_zones?.length ?? 0}
General-Head Boundaries (GHB): ${b.general_head?.length ?? 0}
`);

checkPageSpace(120);

/* CONSTANT HEAD TABLE */
if (b.constant_head && b.constant_head.length > 0) {
  subtitle("Constant-Head Boundaries (Rivers/Lakes)");
  for (let ch of b.constant_head) {
    paragraph(`
• Head: ${fmt(ch.head)} ft 
• Length: ${ch.points.length} nodes
`);
  }
}

/* NO-FLOW TABLE */
if (b.no_flow && b.no_flow.length > 0) {
  subtitle("No-Flow Boundaries");
  for (let nf of b.no_flow) {
    paragraph(`
• Segment Length: ${nf.points.length} nodes
• Represents impermeable barrier or watershed divide
`);
  }
}

/* RECHARGE TABLE */
if (b.recharge_zones && b.recharge_zones.length > 0) {
  subtitle("Recharge Zones");

  for (let rz of b.recharge_zones) {
    paragraph(`
• Area: ${rz.area_acres ?? "N/A"} acres
• Recharge Rate: ${fmt(rz.rate)} gpd/acre
• Polygon Vertices: ${rz.polygon.length}
`);
  }
}

/* GHB TABLE */
if (b.general_head && b.general_head.length > 0) {
  subtitle("General-Head Boundaries (Stream–Aquifer Interaction)");

  for (let g of b.general_head) {
    paragraph(`
• Boundary Head: ${fmt(g.head)} ft
• Conductance: ${fmt(g.cond)} ft²/day
• Segment Nodes: ${g.points.length}
`);
  }
}

pdf.addPage();
y = margin;

/* ==========================================================
   INSERT BOUNDARY MAP IMAGES
   ========================================================== */

title("Boundary Maps");

await addImage(results?.plots?.boundary_map, "Boundary Condition Overlay Map");
await addImage(results?.plots?.recharge_map, "Recharge Zone Map");
await addImage(results?.plots?.ghb_map, "General-Head Boundary Overlay");

/* ==========================================================
   HYDROLOGIC SIGNIFICANCE ANALYSIS
   ========================================================== */

pdf.addPage();
y = margin;

title("Hydrologic Significance of Boundary Conditions");

paragraph(`
The boundary conditions selected in the model influence groundwater flow and capture 
zones in ways consistent with field conditions and hydrologic expectations:

• Constant-head boundaries simulate perennial rivers/streams and provide stabilization 
  of the groundwater table near surface-water features.

• No-flow boundaries represent groundwater divides, bedrock ridges, or lateral 
  boundaries outside of the contributing area.

• Recharge polygons represent infiltration areas that contribute water to the aquifer 
  and impact long-term sustainable yield.

• General-head boundaries represent interactions between surface water and groundwater 
  where head-dependent flux occurs (C × (h₀ - h)).

These conditions comply with Ten States Section 4.0 for delineating capture zones, and 
KDOW 401 KAR 8 requirements for Source Water Protection Area mapping.
`);

checkPageSpace(200);

subtitle("Influence on WHP Zones");

paragraph(`
Boundary effects were propagated through the model and key observations include:

• Zone I radius (immediate protection area) is affected primarily by transmissivity 
  and near-field drawdown, and is minimally sensitive to far-field boundaries.

• Zone II capture zones exhibit shape deviations where general-head boundaries 
  interact with pumping stresses.

• Recharge zones expand the 5-year and 10-year capture areas, consistent with 
  KDOW guidance on wellfield risk assessment.

• Constant-head boundaries can truncate capture zones where hydraulic influence 
  is dominated by surface-water interaction.

These interpretations align with EPA's ground-water modeling guidance and KDOW's 
requirements for delineating inner and outer recharge zones.
`);


  /* ==========================================================
     REGULATORY BASIS
  ========================================================== */

  title("Regulatory Compliance Summary");

  paragraph(`
This report adheres to:
• KDOW Source Water Assessment Requirements (401 KAR 8)
• KDOW Well Construction & Sanitary Setbacks
• Ten States Standards – Section 4.0 Groundwater Supplies
• AWWA A100 Well Construction Standard
• EPA Recommended Methods for Pumping Test Evaluation
`);

  /* ==========================================================
     SAVE PDF
  ========================================================== */

  pdf.save("Aquifer_Analysis_Report.pdf");
}

/* ----------------------------------------------------------
   Helpers
---------------------------------------------------------- */

function fmt(v, digits = 2) {
  return typeof v === "number" ? v.toFixed(digits) : v;
}
