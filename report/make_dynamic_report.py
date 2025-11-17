import os
import numpy as np
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt
from methods.theis import theis_s
from methods.pump72 import simulate_72hr_test

# ---------------------------------------------------------
# Utility: save figure and return path
# ---------------------------------------------------------
def savefig(name, plt_obj=None):
    outdir = "report/figs"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    if plt_obj is None:
        plt.savefig(path, dpi=200, bbox_inches="tight")
    else:
        plt_obj.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    return path


# ---------------------------------------------------------
# Insert paragraph + PASS/FAIL flag
# ---------------------------------------------------------
def compliance_flag(value, ok, reason):
    status = "PASS" if ok else "FAIL"
    return f"{status} — {reason}: {value}"


# ---------------------------------------------------------
# DIURNAL DEMAND PROFILE (EPA/Ten States style)
# ---------------------------------------------------------
def generate_diurnal_curve(avg_day_gpm):
    """
    Standard community water system diurnal pattern multipliers.
    Reference: EPA Water Demand Patterns, Ten States commentary.
    """

    multipliers = np.array([
        0.6, 0.55, 0.52, 0.50, 0.55, 0.70, 1.00, 1.40,
        1.20, 1.10, 1.00, 0.95, 0.90, 0.95, 1.10, 1.40,
        1.70, 1.60, 1.50, 1.30, 1.10, 0.90, 0.75, 0.65
    ])

    hourly_gpm = avg_day_gpm * multipliers
    return multipliers, hourly_gpm


# ---------------------------------------------------------
# Main Dynamic Report Builder
# ---------------------------------------------------------
def make_dynamic_report(results, outfile="report/aquifer_dynamic_report.docx"):

    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(11)
    add = doc.add_paragraph

    # ---------------------------------------------------------
    # INPUT EXTRACTION
    # ---------------------------------------------------------
    inp = results["inputs"]

    Q_gpm = float(inp["pumping_test"]["Q_gpm"])
    Q_cfs = Q_gpm / 448.831

    t = np.array(inp["pumping_test"]["time_min"], dtype=float)
    s_obs = np.array(inp["pumping_test"]["drawdown_observation_well_ft"], dtype=float)
    s_pw = np.array(inp["pumping_test"]["drawdown_pumping_well_ft"], dtype=float)
    r_obs = float(inp["aquifer"]["observation_well_distance_ft"])
    b = float(inp["aquifer"]["b_ft"])

    # Demand block
    dem = inp.get("demand", {})
    population = float(dem.get("population", 2000))
    gpcd_avg = float(dem.get("gpcd_avg", 100.0))
    pf_md = float(dem.get("peaking_max_day", 1.5))
    pf_mh = float(dem.get("peaking_max_hour", 2.5))
    loss_frac = float(dem.get("loss_fraction", 0.15))
    storage_hrs = float(dem.get("min_storage_hours", 24.0))
    storage_avail = float(dem.get("storage_available_gal", 0))

    avg_day_gpd = population * gpcd_avg
    avg_day_gpm = avg_day_gpd / 1440

    max_day_gpd = avg_day_gpd * pf_md
    max_day_gpm = max_day_gpd / 1440

    max_hour_gpm = avg_day_gpm * pf_md * pf_mh

    Q_required_peak = max_hour_gpm / (1 - loss_frac)
    V_required_day = max_day_gpd / (1 - loss_frac)

    # Analytical results
    theis = results["theis"]
    cj = results["cooper_jacob"]
    neu = results["neuman"]
    rec = results["recovery"]

    # Calibration
    T_cal = float(results["calibrated"]["T"])
    Sy_cal = float(results["calibrated"]["Sy"])

    # Recharge
    recharge = float(results["recharge_gpd"])

    # FEM
    fem = results["fem"]
    h = np.array(fem["h"])
    dx = fem["dx"]
    dy = fem["dy"]
    pump_loc = fem["pump_location"]
    h_min = float(np.nanmin(h))

    # WHP
    whp = results["whp"]

    # ---------------------------------------------------------
    # 0. TITLE PAGE / SUMMARY
    # ---------------------------------------------------------
    doc.add_heading("Hydrogeologic Adequacy Assessment – Dynamic Engineering Report", level=1)
    add(f"Pumping Rate: {Q_gpm:.1f} gpm")
    add(f"Population Basis: {population:,.0f}")
    add("Prepared using analytical, numerical, and regulatory-based methods "
        "consistent with Ten States Standards and KDOW 401 KAR 8.")

    doc.add_page_break()

    # ---------------------------------------------------------
    # 1. GRAPHICS SECTION
    # ---------------------------------------------------------
    doc.add_heading("1. Pumping Test Plots", level=1)

    logt = np.log10(t)
    slope_cj, intercept_cj = np.polyfit(logt, s_obs, 1)
    s_pred_cj = slope_cj * logt + intercept_cj

    t_sec = t * 60.0
    T_ft2_sec = max(theis["T"] / 86400.0, 1e-12)
    s_pred_theis = np.array([theis_s(ts, Q_cfs, T_ft2_sec, theis["S"], r_obs) for ts in t_sec])

    sqrt_t = np.sqrt(t)
    slope_neu, intercept_neu = np.polyfit(sqrt_t, s_obs, 1)
    s_pred_neu = slope_neu * sqrt_t + intercept_neu

    T_cal_sec = max(T_cal / 86400.0, 1e-12)
    s_pred_cal = np.array([theis_s(ts, Q_cfs, T_cal_sec, Sy_cal, r_obs) for ts in t_sec])

    # ---------------------------------------------------------
    # 1A – Pumping Well Drawdown vs Time
    # ---------------------------------------------------------
    plt.figure()
    plt.plot(t, s_pw, "o-", label="Pumping Well")
    plt.xlabel("Time (min)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Pumping Well Drawdown vs Time")
    plt.grid(True)
    p = savefig("pumping_well_drawdown.png")
    doc.add_heading("1.1 Pumping Well Drawdown Curve", level=2)
    doc.add_picture(p, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1B – Observation Well Drawdown vs Time
    # ---------------------------------------------------------
    plt.figure()
    plt.plot(t, s_obs, "o-", color="green")
    plt.xlabel("Time (min)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Observation Well Drawdown vs Time")
    plt.grid(True)
    p = savefig("observation_well_drawdown.png")
    doc.add_heading("1.2 Observation Well Drawdown Curve", level=2)
    doc.add_picture(p, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1C – Cooper-Jacob Semilog Plot
    # ---------------------------------------------------------
    plt.figure()
    plt.semilogx(t, s_obs, "o", label="Observed")
    plt.semilogx(t, s_pred_cj, "-", label="CJ Fit")
    plt.xlabel("Time (min, log scale)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Cooper–Jacob Straight-Line Plot")
    plt.grid(True)
    plt.legend()
    p = savefig("cooper_jacob_fit.png")
    doc.add_heading("1.3 Cooper–Jacob Plot", level=2)
    doc.add_picture(p, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1D – Theis Fit Plot
    # ---------------------------------------------------------
    plt.figure()
    plt.plot(t, s_obs, "o", label="Observed")
    plt.plot(t, s_pred_theis, "-", label="Theis Fit")
    plt.xlabel("Time (min)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Theis Curve Fit")
    plt.grid(True)
    plt.legend()
    p = savefig("theis_fit.png")
    doc.add_heading("1.4 Theis Fit Plot", level=2)
    doc.add_picture(p, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1E – Neuman Fit Plot
    # ---------------------------------------------------------
    plt.figure()
    plt.plot(t, s_obs, "o", label="Observed")
    plt.plot(t, s_pred_neu, "-", label="Neuman Fit")
    plt.xlabel("Time (min)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Neuman Delayed Yield Fit")
    plt.grid(True)
    plt.legend()
    p = savefig("neuman_fit.png")
    doc.add_heading("1.5 Neuman Fit Plot", level=2)
    doc.add_picture(p, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1F – FEM Contours
    # ---------------------------------------------------------
    # FEM contour is already generated externally; we embed it here
    contour_file = "report/drawdown_contours.png"
    if os.path.exists(contour_file):
        doc.add_heading("1.6 Numerical Model Contours", level=2)
        doc.add_picture(contour_file, width=Inches(5.5))

    # ---------------------------------------------------------
    # 1G – Calibration Fit
    # ---------------------------------------------------------
    plt.figure()
    plt.plot(t, s_obs, "o", label="Observed")
    plt.plot(t, s_pred_cal, "-", label="Calibrated Fit")
    plt.xlabel("Time (min)")
    plt.ylabel("Drawdown (ft)")
    plt.title("Calibrated Parameter Fit")
    plt.grid(True)
    plt.legend()
    p = savefig("calibration_fit.png")
    doc.add_heading("1.7 Calibration Fit", level=2)
    doc.add_picture(p, width=Inches(5.5))

    doc.add_page_break()

    # ---------------------------------------------------------
    # 2. DIURNAL DEMAND + WELL OPERATIONAL SCHEDULE
    # ---------------------------------------------------------
    doc.add_heading("2. Diurnal Demand Curve and Pumping Schedule", level=1)

    multipliers, hourly_gpm = generate_diurnal_curve(avg_day_gpm)

    # Plot demand curve
    hours = np.arange(24)

    plt.figure()
    plt.plot(hours, hourly_gpm, "o-", label="Demand")
    plt.xlabel("Hour of Day")
    plt.ylabel("Flow (gpm)")
    plt.title("Diurnal Demand Curve")
    plt.grid(True)
    p = savefig("diurnal_demand.png")
    doc.add_picture(p, width=Inches(5.5))

    # Compute pumping schedule
    pump_rate = Q_gpm
    storage = storage_avail

    tank = storage
    hourly_source = []
    hourly_tank = []

    for h in range(24):
        demand = hourly_gpm[h]

        if pump_rate >= demand:
            # well more than meets demand
            net = pump_rate - demand
            tank += net * 60
            source = demand
        else:
            # well alone is insufficient → pull from tank if available
            deficit = demand - pump_rate
            tank -= deficit * 60
            source = pump_rate

        hourly_tank.append(tank)
        hourly_source.append(source)

    # Plot tank level pattern
    plt.figure()
    plt.plot(hours, hourly_tank, "o-")
    plt.xlabel("Hour of Day")
    plt.ylabel("Tank Volume (gal)")
    plt.title("Daily Tank Volume Pattern")
    plt.grid(True)
    p = savefig("tank_volume_pattern.png")
    doc.add_picture(p, width=Inches(5.5))

    # Plot pumping schedule
    plt.figure()
    plt.plot(hours, hourly_source, "o-", label="Source Output (gpm)")
    plt.plot(hours, hourly_gpm, "--", label="Demand (gpm)")
    plt.xlabel("Hour")
    plt.ylabel("Flow (gpm)")
    plt.title("Well Pumping vs. Demand")
    plt.legend()
    plt.grid(True)
    p = savefig("pumping_schedule.png")
    doc.add_picture(p, width=Inches(5.5))

    # Identify pumping vs idle
    doc.add_heading("2.4 Pumping Schedule Summary", level=2)
    for h in range(24):
        if pump_rate >= hourly_gpm[h]:
            add(f"Hour {h}: Well OFF or low-speed (demand {hourly_gpm[h]:.1f} gpm)")
        else:
            add(f"Hour {h}: Well ON (demand {hourly_gpm[h]:.1f} gpm > {pump_rate:.1f} gpm)")

    doc.add_page_break()

    # ---------------------------------------------------------
    # 3. 72-Hour Sustained Pump Test Simulation
    # ---------------------------------------------------------
    doc.add_heading("3. 72-Hour Sustained Pump Test", level=1)
    S_for_72 = max(theis["S"], 1e-6)
    times72, draw72 = simulate_72hr_test(Q_cfs, T_cal_sec, S_for_72, r_obs)
    hours72 = times72 / 60.0
    plt.figure()
    plt.plot(hours72, draw72, label="Drawdown / Recovery")
    plt.xlabel("Time (hours)")
    plt.ylabel("Drawdown (ft)")
    plt.title("72-Hour Pumping + Recovery Simulation")
    plt.grid(True)
    p = savefig("pump_test_72hr.png")
    doc.add_picture(p, width=Inches(5.5))
    doc.add_paragraph(
        f"Simulated maximum drawdown: {float(np.max(draw72)):.2f} ft; "
        f"recovery rebound: {float(np.max(np.abs(draw72[draw72 < 0]))) if np.any(draw72 < 0) else 0:.2f} ft."
    )
    results["pump72_summary"] = {
        "max_drawdown_ft": float(np.max(draw72)),
        "min_drawdown_ft": float(np.min(draw72)),
        "times_min": times72.tolist(),
        "drawdown_ft": draw72.tolist()
    }

    doc.add_page_break()

    # ---------------------------------------------------------
    # 4. Multi-Well Interference
    # ---------------------------------------------------------
    doc.add_heading("4. Multi-Well Interference Modeling", level=1)
    interference = results.get("interference")
    if interference and interference.get("drawdown_ft"):
        times_multi = np.array(interference["times_min"])
        draw_multi = np.array(interference["drawdown_ft"])
        plt.figure()
        plt.plot(times_multi, draw_multi, label="Interference drawdown")
        plt.xlabel("Time (min)")
        plt.ylabel("Drawdown (ft)")
        plt.title("Multi-Well Interference Response")
        plt.grid(True)
        p = savefig("multiwell_interference.png")
        doc.add_picture(p, width=Inches(5.5))
        doc.add_paragraph(
            f"Peak mutual drawdown: {interference.get('peak_drawdown_ft', float(np.max(draw_multi))):.2f} ft at "
            f"{interference.get('observation_distance_ft', r_obs):.0f} ft from the pumping center."
        )
    else:
        doc.add_paragraph("No multi-well interference dataset supplied.")

    doc.add_page_break()

    # ---------------------------------------------------------
    # 5. Extended Engineering Narrative
    # ---------------------------------------------------------
    from report.make_dynamic_report_coretext import add_core_text
    add_core_text(doc, results)

    doc.save(outfile)
    print(f"\nDynamic graphical report saved to: {outfile}\n")
