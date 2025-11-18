from docx import Document
from docx.shared import Pt
import numpy as np


def compliance_flag(value, ok, reason):
    """Returns formatted string with PASS/FAIL and reason."""
    status = "PASS" if ok else "FAIL"
    return f"{status} — {reason}: {value}"


def make_dynamic_report(results, outfile="report/aquifer_dynamic_report.docx"):
    """
    Create a fully dynamic narrative report based on:
        - analytical methods
        - calibration results
        - recharge
        - FEM
        - WHP
        - demand vs source adequacy

    'results' dictionary must include:
        {
            "inputs": {...},
            "theis": {...},
            "cooper_jacob": {...},
            "neuman": {...},
            "recovery": {...},
            "calibrated": {"T":..., "Sy":...},
            "recharge_gpd": ...,
            "fem": {"h":..., "dx":..., "dy":...},
            "whp": {...}
        }
    """

    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(11)
    add = doc.add_paragraph

    # ---------------------------------------------
    # Extract / compute base values
    # ---------------------------------------------
    inp = results["inputs"]

    # Pumping & aquifer
    Q_gpm = inp["pumping_test"]["Q_gpm"]
    Q_cfs = Q_gpm / 448.831
    t = np.array(inp["pumping_test"]["time_min"])
    s_obs = np.array(inp["pumping_test"]["drawdown_observation_well_ft"])
    s_pw = np.array(inp["pumping_test"]["drawdown_pumping_well_ft"])
    b = inp["aquifer"]["b_ft"]
    r_obs = inp["aquifer"]["observation_well_distance_ft"]

    # Demand block (with defaults)
    demand_cfg = inp.get("demand", {})
    population = demand_cfg.get("population", 2000)
    gpcd_avg = demand_cfg.get("gpcd_avg", 100.0)
    pf_max_day = demand_cfg.get("peaking_max_day", 1.5)
    pf_max_hour = demand_cfg.get("peaking_max_hour", 2.5)
    loss_frac = demand_cfg.get("loss_fraction", 0.15)
    min_storage_hours = demand_cfg.get("min_storage_hours", 24.0)

    theis = results["theis"]
    cj = results["cooper_jacob"]
    neu = results["neuman"]
    rec = results["recovery"]

    T_cal = results["calibrated"]["T"]
    Sy_cal = results["calibrated"]["Sy"]
    recharge = results["recharge_gpd"]
    fem = results["fem"]
    whp = results["whp"]

    h = fem["h"]
    hw = float(np.nanmin(h))

    # Basic performance metrics
    s_pw_final = float(s_pw[-1]) if len(s_pw) > 0 else 0.0
    sc = Q_gpm / s_pw_final if s_pw_final > 0 else 0.0
    dd_frac = s_pw_final / b if b > 0 else 0.0

    # ----------------------------
    # Demand calculations
    # ----------------------------
    # Average day demand (gpd)
    avg_day_gpd = population * gpcd_avg
    avg_day_gpm = avg_day_gpd / 1440.0

    # Max day demand
    max_day_gpd = avg_day_gpd * pf_max_day
    max_day_gpm = max_day_gpd / 1440.0

    # Max hour demand (based on avg day with peaking factors)
    max_hour_gpm = avg_day_gpm * pf_max_day * pf_max_hour

    # Include losses (source must produce more to cover losses)
    # Source demand at peak hour:
    Q_required_peak_gpm = max_hour_gpm / (1.0 - loss_frac)

    # Daily volume required at source (include losses)
    daily_required_gpd = max_day_gpd / (1.0 - loss_frac)

    # Well capacity at test rate (no SF applied here; you can add a safety factor)
    Q_source_gpm = Q_gpm
    daily_source_gpd = Q_source_gpm * 1440.0

    # Storage requirement: simple rule = one avg day of demand
    # (You can refine this to Ten States equalizing + fire + emergency)
    storage_required_gal = avg_day_gpd  # 1 day of avg demand
    # Approx storage that would be needed if we only want the well
    # to cover peak hour deficits — for now, we just compare required vs "assumed"
    # (actual tank volumes would be another input)
    storage_available_gal = demand_cfg.get("storage_available_gal", 0.0)

    # ----------------------------
    # Compliance checks
    # ----------------------------
    ok_dd = dd_frac < 0.5                   # drawdown < 50% of thickness
    ok_sc = sc > 5.0                        # specific capacity > 5 gpm/ft
    ok_T = T_cal > 5.0                      # minimal T adequacy screen
    ok_whp = whp["zone1_radius_ft"] < 5000  # reasonable primary WHP radius
    ok_fem = hw > 0.0                       # head above base (simplified)

    # Instantaneous capacity: can well meet peak hour?
    ok_peak_inst = Q_source_gpm >= Q_required_peak_gpm

    # Daily volume: can well produce needed daily volume?
    ok_daily_vol = daily_source_gpd >= daily_required_gpd

    # Storage: check if available storage meets suggested minimum
    ok_storage = storage_available_gal >= storage_required_gal

    # Overall demand adequacy flag
    demand_ok = ok_peak_inst and ok_daily_vol and (ok_storage or storage_available_gal == 0.0)

    overall = ok_dd and ok_sc and ok_T and ok_whp and ok_fem and demand_ok

    # ============================================================
    #  TITLE
    # ============================================================
    doc.add_heading("Hydrogeologic Evaluation & Adequacy for Public Supply", level=1)

    add(f"Proposed Withdrawal Rate: {Q_gpm} gpm")
    add(f"Observation Well Distance: {r_obs} ft")
    add(f"Aquifer Thickness: {b} ft")
    add(f"Population Basis: {population} persons (design)")

    # ============================================================
    #  SECTION 1 — Aquifer Hydraulic Properties
    # ============================================================
    doc.add_heading("1. Aquifer Hydraulic Properties", level=2)

    add(f"Theis Method: T = {theis['T']:.1f} ft²/day, S = {theis['S']:.3f}")
    add(f"Cooper–Jacob: T = {cj['T']:.1f} ft²/day, S = {cj['S']:.1f}")
    add(f"Neuman Unconfined: T = {neu['T']:.1f} ft²/day, Sy = {neu['Sy']:.3f}")
    add(f"Recovery Method: T = {rec['T']:.2f} ft²/day")

    add(f"Calibrated Parameters for Simulation: T_cal = {T_cal:.2f} ft²/day, Sy_cal = {Sy_cal:.3f}")

    # ============================================================
    #  SECTION 2 — Hydrogeologic Compliance Screening
    # ============================================================
    doc.add_heading("2. Hydrogeologic Compliance Screening", level=2)

    add(compliance_flag(f"{dd_frac*100:.1f}% of thickness",
                        ok_dd,
                        "Drawdown fraction (<50% of saturated thickness)"))

    add(compliance_flag(f"{sc:.1f} gpm/ft",
                        ok_sc,
                        "Specific capacity (>5 gpm/ft typical minimum)"))

    add(compliance_flag(f"T_cal = {T_cal:.1f} ft²/day",
                        ok_T,
                        "Transmissivity adequate for community supply"))

    add(compliance_flag(f"Zone 1 radius = {whp['zone1_radius_ft']:.0f} ft",
                        ok_whp,
                        "Reasonable primary WHP zone extent"))

    add(compliance_flag(f"Minimum modeled head = {hw:.2f} (relative units)",
                        ok_fem,
                        "Modeled heads remain above aquifer base"))

    # ============================================================
    #  SECTION 3 — Recharge Screening
    # ============================================================
    doc.add_heading("3. Recharge Screening", level=2)

    add(f"Estimated Recharge Rate (screening): {recharge:,.0f} gpd per acre")
    add("Recharge is used as a screening check; transmissivity and available drawdown "
        "are generally more limiting than basin-wide recharge for the proposed rate.")

    # ============================================================
    #  SECTION 4 — Demand & Storage Calculations
    # ============================================================
    doc.add_heading("4. Demand and Storage Calculations (EPA/Ten States Style)", level=2)

    add(f"Average Day Demand: {avg_day_gpd:,.0f} gpd "
        f"({avg_day_gpm:,.1f} gpm) "
        f"at {gpcd_avg:.0f} gpcd for {population} people.")

    add(f"Maximum Day Demand (PF = {pf_max_day:.2f}): {max_day_gpd:,.0f} gpd "
        f"({max_day_gpm:,.1f} gpm).")

    add(f"Maximum Hour Demand (PF = {pf_max_day:.2f} × {pf_max_hour:.2f}): "
        f"{max_hour_gpm:,.1f} gpm (at the customer side).")

    add(f"Assumed Water Loss: {loss_frac*100:.1f}%")

    add(f"Required Source Peak Capacity (including losses): "
        f"{Q_required_peak_gpm:,.1f} gpm.")

    add(f"Required Daily Source Volume (including losses): "
        f"{daily_required_gpd:,.0f} gpd.")

    add(f"Well Capacity at Test Rate: {Q_source_gpm:,.1f} gpm "
        f"({daily_source_gpd:,.0f} gpd per day).")

    add(f"Minimum Suggested Storage (1 × average day): "
        f"{storage_required_gal:,.0f} gallons.")

    if storage_available_gal > 0:
        add(f"Available Storage (input): {storage_available_gal:,.0f} gallons.")
    else:
        add("Available Storage: not specified in input (assumed to be addressed "
            "in separate storage design calculations).")

    # Demand compliance flags
    doc.add_heading("4.1 Demand vs Source Compliance Checks", level=3)

    add(compliance_flag(f"Q_source = {Q_source_gpm:,.1f} gpm, "
                        f"Q_required_peak = {Q_required_peak_gpm:,.1f} gpm",
                        ok_peak_inst,
                        "Instantaneous peak-hour capacity"))

    add(compliance_flag(f"Daily source = {daily_source_gpd:,.0f} gpd, "
                        f"daily required = {daily_required_gpd:,.0f} gpd",
                        ok_daily_vol,
                        "Daily volume adequacy (max day + losses)"))

    if storage_available_gal > 0:
        add(compliance_flag(f"Storage available = {storage_available_gal:,.0f} gal, "
                            f"min suggested = {storage_required_gal:,.0f} gal",
                            ok_storage,
                            "Equalizing/emergency storage (1 × average day)"))
    else:
        add("Storage PASS/FAIL not evaluated because storage volume was not provided; "
            "final compliance will depend on tank design per Ten States and KDOW.")

    # ============================================================
    #  SECTION 5 — Adequacy for Public Supply (Dynamic Narrative)
    # ============================================================
    doc.add_heading("5. Adequacy for Public Supply", level=2)

    narrative = []

    narrative.append(
        "Based on the aquifer hydraulic properties derived from the pumping test "
        "(transmissivity and storativity/specific yield), the observed drawdowns in "
        "the pumping and observation wells, the recharge screening estimate, and "
        "the calibrated numerical model, the source aquifer demonstrates the "
        "ability to sustain the proposed withdrawal rate under typical conditions."
    )

    # Highlight hydrogeo caveats
    if not ok_T:
        narrative.append(
            "The calibrated transmissivity is relatively low compared to typical "
            "values for high-yield community supply wells. KDOW may require "
            "additional conservative assumptions, operating restrictions, or "
            "supplemental data to confirm long-term reliability."
        )

    if not ok_whp:
        narrative.append(
            "The calculated primary wellhead protection (Zone 1) radius is large "
            "relative to common KDOW expectations, suggesting that either "
            "transmissivity is low or drawdown (Δh) may be overestimated. "
            "The WHP delineation should be refined as part of the Source Water "
            "Protection Plan."
        )

    # Demand-based caveats
    if not ok_peak_inst:
        narrative.append(
            "At the current test pumping rate, the well does not meet the "
            "instantaneous capacity required to satisfy the calculated maximum "
            "hour demand (including system losses). Either additional source "
            "capacity, revised peaking assumptions, or storage must be provided."
        )

    if not ok_daily_vol:
        narrative.append(
            "On a daily basis, the total volume that can be produced at the test "
            "rate is less than the calculated maximum day demand (including losses). "
            "Long-term operation at this population and demand level would not be "
            "sustainable without additional sources or reduced demand."
        )

    if storage_available_gal > 0 and not ok_storage:
        narrative.append(
            "The available storage volume appears to be less than one average day "
            "of demand, which is commonly used as a screening criterion for "
            "equalizing and emergency storage. Storage design should be evaluated "
            "against Ten States Standards and KDOW requirements."
        )

    # Final overall statement
    if overall:
        narrative.append(
            "Overall, the available data indicate that the aquifer and well, in "
            "combination with reasonable storage provisions, are adequate to "
            "meet the projected demands of the service population, subject to "
            "final review and approval by the Kentucky Division of Water under "
            "401 KAR 8:020 and 401 KAR 8:150."
        )
    else:
        narrative.append(
            "One or more hydrogeologic or demand-related criteria did not meet "
            "typical regulatory expectations. Additional investigation, "
            "conservative operating assumptions, supplementary sources, and/or "
            "increased storage will likely be required to demonstrate compliance "
            "for long-term public water supply use."
        )

    for p in narrative:
        add(p)

    # ============================================================
    #  SAVE REPORT
    # ============================================================
    doc.save(outfile)
    print(f"\nDynamic report saved to: {outfile}\n")
