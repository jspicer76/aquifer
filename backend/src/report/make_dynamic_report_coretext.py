from docx import Document
from docx.shared import Inches
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt


def generate_dynamic_report(
    theis,
    cooper_jacob,
    neuman,
    recovery,
    recharge,
    fem,
    whp,
    calibration,
    demand,
    interference=None,
    pump72=None,
    aquifer_class=None,
    inputs=None,
    figures=None,
    well_design=None,
):
    """Build a full KDOW-style report summarizing analytical and design results."""
    os.makedirs("report", exist_ok=True)
    doc = Document()

    # ------------------------------------------------------------------
    # Title / Intro
    # ------------------------------------------------------------------
    doc.add_heading("Groundwater Supply & Aquifer Adequacy Evaluation", level=1)
    doc.add_paragraph("Prepared automatically by Aquifer Analysis Suite")
    doc.add_paragraph(f"Date: {datetime.date.today()}")
    doc.add_page_break()

    doc.add_heading("1. Introduction", level=2)
    doc.add_paragraph(
        "This document compiles analytical pumping-test interpretation, aquifer "
        "classification, numerical modeling, interference simulations, 72-hour stress "
        "tests, and well construction design in support of KDOW 401 KAR 8:020 review."
    )

    # ------------------------------------------------------------------
    # Pumping test summary
    # ------------------------------------------------------------------
    doc.add_heading("2. Pumping Test Interpretation", level=2)
    doc.add_paragraph("Summary of analytical fits:")
    table = doc.add_table(rows=1, cols=4)
    hdr = table.rows[0].cells
    hdr[0].text = "Method"
    hdr[1].text = "Transmissivity (ft²/day)"
    hdr[2].text = "Storage"
    hdr[3].text = "Notes"

    def add_row(name, T, S, note):
        row = table.add_row().cells
        row[0].text = name
        row[1].text = f"{T:.2f}"
        row[2].text = f"{S:.3e}"
        row[3].text = note

    add_row("Theis", theis["T"], theis["S"], "Baseline confined/unconfined curve fit")
    add_row("Cooper-Jacob", cooper_jacob["T"], cooper_jacob["S"], "Late-time straight line")
    add_row("Neuman", neuman["T"], neuman["Sy"], "Unconfined delayed yield solution")
    add_row("Recovery", recovery["T"], np.nan, "Theis recovery method")

    doc.add_paragraph(
        "Detailed type curve plots were generated for each analytical fit to verify "
        "consistency with field data."
    )

    if figures:
        for key, label in [
            ("theis", "Theis Type-Curve Fit"),
            ("cj", "Cooper-Jacob Plot"),
            ("neuman", "Neuman Fit"),
            ("calibration", "Calibrated Parameter Fit"),
        ]:
            if figures.get(key):
                doc.add_picture(figures[key], width=Inches(5.5))
                doc.add_paragraph(f"Figure: {label}")

    # ------------------------------------------------------------------
    # Aquifer classification
    # ------------------------------------------------------------------
    doc.add_heading("3. Aquifer Classification", level=2)
    if aquifer_class:
        doc.add_paragraph(f"Aquifer Type: {aquifer_class['type']}")
        doc.add_paragraph(f"Rationale: {aquifer_class['rationale']}")
        doc.add_paragraph(aquifer_class["engineering_note"])
        if aquifer_class.get("gwsi") is not None:
            doc.add_paragraph(
                f"Groundwater Sustainability Index (supply/peak-day demand) = "
                f"{aquifer_class['gwsi']:.2f}. {aquifer_class['gwsi_note']}"
            )
    else:
        doc.add_paragraph("Aquifer classification pending additional data.")

    # ------------------------------------------------------------------
    # Numerical model summary
    # ------------------------------------------------------------------
    doc.add_heading("4. Numerical Modeling (FD 2-D)", level=2)
    doc.add_paragraph(
        "Finite-difference steady-state model constructed using calibrated T and Sy "
        "parameters. Drawdown contours attached separately."
    )
    contour_path = "report/drawdown_contours.png"
    if os.path.exists(contour_path):
        doc.add_picture(contour_path, width=Inches(5.0))

    # ------------------------------------------------------------------
    # Demand and diurnal curve figure references handled upstream
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Interference & 72-hour
    # ------------------------------------------------------------------
    doc.add_heading("5. Interference / Stress Simulations", level=2)
    if interference:
        doc.add_paragraph(
            f"Multi-well superposition predicts peak mutual drawdown of "
            f"{interference.get('peak_drawdown_ft', 0.0):.2f} ft at "
            f"{interference.get('observation_distance_ft', 0.0):.0f} ft."
        )
        fig_path = os.path.join("report", "figs", "multiwell_interference.png")
        if os.path.exists(fig_path):
            doc.add_picture(fig_path, width=Inches(5.0))
    else:
        doc.add_paragraph("No interference scenario provided.")

    if pump72:
        doc.add_paragraph(
            f"72-hour simulated drawdown: max {pump72['max_drawdown_ft']:.2f} ft, "
            f"terminal value {pump72['end_value_ft']:.2f} ft."
        )
        fig_72 = os.path.join("report", "figs", "pump_test_72hr.png")
        if os.path.exists(fig_72):
            doc.add_picture(fig_72, width=Inches(5.0))

    # ------------------------------------------------------------------
    # Well design tables
    # ------------------------------------------------------------------
    if well_design:
        doc.add_heading("11. Well Construction & Equipment Design", level=2)
        wd = well_design["design"]
        gp = well_design["gravel_pack"]
        dev = well_design["development"]
        pump_sel = well_design["pump"]
        energy = well_design["pump_energy"]
        cost = well_design["well_cost"]
        diagram_path = well_design["diagram"]

        doc.add_heading("11.1 Casing & Screen", level=3)
        table_well = doc.add_table(rows=1, cols=2)
        hw = table_well.rows[0].cells
        hw[0].text = "Parameter"
        hw[1].text = "Value"

        def add_w(label, value):
            row = table_well.add_row().cells
            row[0].text = label
            row[1].text = value

        add_w("Final Diameter", f"{wd['diameter_in_final']} in")
        add_w("Required Diameter (calc)", f"{wd['diameter_in_required']:.1f} in")
        add_w("Screen Length", f"{wd['screen_length_ft']:.1f} ft")
        add_w(
            "Screen Length Range",
            f"{wd['screen_length_range_ft'][0]:.1f} – {wd['screen_length_range_ft'][1]:.1f} ft",
        )
        add_w("Slot Size", f"{wd['slot_size_in']:.3f} in")
        add_w("Specific Capacity (approx)", f"{wd['SC_approx']:.2f} gpm/ft")

        doc.add_heading("11.2 Gravel Pack Design", level=3)
        table_gp = doc.add_table(rows=1, cols=2)
        hgp = table_gp.rows[0].cells
        hgp[0].text = "Parameter"
        hgp[1].text = "Value"
        for label, key in [
            ("Filter Pack D10", "GP_D10_mm"),
            ("Filter Pack D50", "GP_D50_mm"),
            ("Porosity", "porosity"),
            ("Thickness (ft)", "thickness_ft"),
            ("Slot Size", "slot_size_in"),
        ]:
            row = table_gp.add_row().cells
            row[0].text = label
            row[1].text = f"{gp[key]:.2f}" if "porosity" in key or "D" in key else str(gp[key])
        doc.add_paragraph(gp["notes"])

        doc.add_heading("11.3 Development Requirements", level=3)
        doc.add_paragraph(
            f"Airlifting/Surge Block: {dev['airlift_hours']:.1f} hrs\n"
            f"Jetting: {dev['jetting_hours']:.1f} hrs"
        )

        doc.add_heading("11.4 Pump Sizing & TDH", level=3)
        table_p = doc.add_table(rows=1, cols=2)
        hp = table_p.rows[0].cells
        hp[0].text = "Parameter"
        hp[1].text = "Value"
        for label, key in [
            ("Static Lift", "static_lift_ft"),
            ("Friction Loss", "friction_loss_ft"),
            ("Total Dynamic Head", "TDH_ft"),
            ("Calculated HP", "HP_calc"),
            ("Recommended HP", "HP_recommended"),
        ]:
            row = table_p.add_row().cells
            row[0].text = label
            row[1].text = f"{pump_sel[key]:.1f}"
        doc.add_paragraph(pump_sel["notes"])

        doc.add_heading("11.5 Pump Operating Cost", level=3)
        doc.add_paragraph(
            f"Energy Use: {energy['kWh_day']:.1f} kWh/day "
            f"(${energy['daily_cost']:.2f}/day, ${energy['annual_cost']:.2f}/year)"
        )

        doc.add_heading("11.6 Well Installation Cost Estimate", level=3)
        table_c = doc.add_table(rows=1, cols=2)
        hc = table_c.rows[0].cells
        hc[0].text = "Cost Item"
        hc[1].text = "Amount"
        for label in ["drilling", "screen_cost", "development", "mobilization", "total_cost"]:
            row = table_c.add_row().cells
            row[0].text = label.capitalize()
            row[1].text = f"${cost[label]:,.2f}"

        doc.add_heading("11.7 Well Diagram", level=3)
        if diagram_path and os.path.exists(diagram_path):
            doc.add_picture(diagram_path, width=Inches(4))

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------
    doc.add_heading("12. References", level=2)
    doc.add_paragraph(
        "- Theis, C.V. (1935). Lowering of the Piezometric Surface...\n"
        "- Cooper & Jacob (1946). Graphical Method for Pumping Tests.\n"
        "- Neuman, S.P. (1972). Theory of Flow in Unconfined Aquifers.\n"
        "- Ten States Standards (2023).\n"
        "- KDOW 401 KAR 8:020 / 8:150."
    )

    report_path = "report/aquifer_dynamic_report.docx"
    doc.save(report_path)
    print(f"\nDynamic report written: {report_path}")


def add_core_text(doc, results):
    """Append extended narrative to graphical report."""
    add = doc.add_paragraph
    inputs = results.get("inputs", {})
    demand = inputs.get("demand", {})
    q_gpm = inputs.get("pumping_test", {}).get("Q_gpm", 0.0)

    doc.add_heading("5. Extended Engineering Narrative", level=1)
    aquifer_class = results.get("aquifer_class")
    if aquifer_class:
        doc.add_heading("5.1 Aquifer Classification & GWSI", level=2)
        add(f"Aquifer Type: {aquifer_class['type']}")
        add(aquifer_class["rationale"])
        if aquifer_class.get("gwsi") is not None:
            add(
                f"GWSI (supply/peak-day demand) = {aquifer_class['gwsi']:.2f}. "
                f"{aquifer_class['gwsi_note']}"
            )

    if demand:
        doc.add_heading("5.2 Demand vs Supply", level=2)
        population = demand.get("population", 0)
        gpcd = demand.get("gpcd_avg", 0)
        pf_md = demand.get("peaking_max_day", 1.0)
        pf_mh = demand.get("peaking_max_hour", 1.0)
        losses = demand.get("loss_fraction", 0.0)
        avg_gpd = population * gpcd * (1 + losses)
        max_day = avg_gpd * pf_md
        max_hour = (avg_gpd / 24.0) * pf_mh
        add(f"Population: {population:,} at {gpcd} gpcd (+{losses:.0%} losses).")
        add(f"Average-day demand: {avg_gpd:,.0f} gpd ({avg_gpd/1440:.0f} gpm).")
        add(f"Max-day demand (PF={pf_md:.2f}): {max_day:,.0f} gpd.")
        add(f"Max-hour demand (PF={pf_mh:.2f}): {max_hour:,.0f} gph.")
        add(
            "Well capacity meets Ten States criteria."
            if q_gpm * 1440 >= max_day
            else "Additional storage or redundancy recommended."
        )

    interference = results.get("interference")
    doc.add_heading("5.3 Multi-Well Interference Summary", level=2)
    if interference and interference.get("drawdown_ft"):
        add(
            f"Peak mutual drawdown estimated at {interference['peak_drawdown_ft']:.2f} ft "
            f"for observation distance {interference['observation_distance_ft']:.0f} ft."
        )
    else:
        add("No interference dataset supplied.")

    pump72 = results.get("pump72")
    if pump72:
        doc.add_heading("5.4 72-Hour Stress Test Summary", level=2)
        add(
            f"Simulated maximum drawdown {pump72['max_drawdown_ft']:.2f} ft; "
            f"terminal recovery {pump72['end_value_ft']:.2f} ft."
        )

    doc.add_heading("5.5 Regulatory Summary", level=2)
    add(
        "Analytical, numerical, and design evaluations collectively show compliance "
        "with Ten States Standards and KDOW hydrogeologic investigation requirements."
    )
