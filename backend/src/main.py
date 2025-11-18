import json
import os
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Analytical Methods
# -------------------------------
from .solver.methods.theis import theis_fit, theis_s
from .solver.methods.cooper_jacob import cooper_jacob_fit
from .solver.methods.neuman import neuman_fit
from .solver.methods.recovery import recovery_fit
from .solver.methods.interference import multiwell_timeseries
from .solver.methods.pump72 import simulate_72hr_test
from .solver.designer.well_designer import design_well


# -------------------------------
# FEM Model & Plotting
# -------------------------------
from .solver.fem.fd2d_solver import run_fd2d_model
from .solver.fem.plot_contours import plot_drawdown_contours
from .solver.fem.whp import compute_whp_zones

# -------------------------------
# KDOW SWA-2 Form
# -------------------------------
from .report.fill_swa2 import fill_swa2_form

# -------------------------------
# Calibration Engine
# -------------------------------
from .solver.methods.calibration import calibrate_parameters

# --------------------------------------------------
# WELL DESIGN MODULES
# --------------------------------------------------
from .solver.designer.gravel_pack import design_gravel_pack
from .solver.designer.development import estimate_well_development_time
from .solver.designer.pump_selector import pump_selection
from .solver.designer.cost_estimator import estimate_well_cost, pump_energy_cost
from .solver.designer.well_diagram import make_well_diagram

# ======================================================
# AQUIFER TYPE CLASSIFICATION
# ======================================================
def classify_aquifer(T, S, Sy):
    """
    Classify aquifer as confined, unconfined, or leaky based on
    storativity (S), specific yield (Sy), and transmissivity (T).

    References:
      - Kruseman & de Ridder (1990)
      - Fetter (Applied Hydrogeology, 4th ed.)
      - U.S. EPA Pumping Test Guidelines (2018)
    """

    confined_S_max = 1e-3        # Confined S typically 1e-5 to 1e-3
    unconfined_Sy_min = 0.05     # Water-table Sy typically 0.05 to 0.30+

    if S < confined_S_max and Sy < 0.02:
        aquifer_type = "Confined Aquifer"
        rationale = (
            f"S ({S:.2e}) is within the typical confined range (<1e-3) "
            f"and Sy ({Sy:.3f}) is too low for an unconfined system."
        )
    elif Sy >= unconfined_Sy_min:
        aquifer_type = "Unconfined Aquifer"
        rationale = (
            f"Specific yield Sy ({Sy:.3f}) falls within the unconfined range "
            f"(0.05-0.35). Storativity S ({S:.2e}) is also higher than values "
            f"expected for confined systems."
        )
    else:
        aquifer_type = "Leaky / Semi-Confined Aquifer"
        rationale = (
            f"S ({S:.2e}) and Sy ({Sy:.3f}) fall between confined and unconfined "
            f"ranges, indicating possible vertical leakage through a semi-confining layer."
        )

    engineering_note = (
        "Classification is based solely on hydraulic response. "
        "Final designation should be supported by lithology, well construction, "
        "and regional hydrogeologic mapping."
    )

    return {
        "type": aquifer_type,
        "rationale": rationale,
        "engineering_note": engineering_note
    }

# -------------------------------
# Dynamic Report Writer
# -------------------------------
from .report.make_dynamic_report import make_dynamic_report



# ======================================================
# LOAD INPUT DATA
# ======================================================
def load_inputs():
    """Load aquifer input JSON safely."""
    filename = "aquifer_input.json"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = os.path.join(base_dir, filename)
    print("USING INPUT FILE:", abs_path)

    with open(abs_path, "r", encoding="utf-8-sig") as f:
        raw = f.read()

    if raw.strip() == "":
        raise ValueError("ERROR: aquifer_input.json is empty.")

    print("---- FIRST 200 CHARS OF INPUT ----")
    print(repr(raw[:200]))
    print("-----------------------------------")

    return json.loads(raw)



# ======================================================
# MAIN PIPELINE
# ======================================================
def main():

    # --------------------------------------------------
    # Load JSON Input
    # --------------------------------------------------
    data = load_inputs()

    # Pumping Test Inputs
    Q_gpm = data["pumping_test"]["Q_gpm"]
    Q_cfs = Q_gpm / 448.831

    t = np.array(data["pumping_test"]["time_min"])
    s_obs = np.array(data["pumping_test"]["drawdown_observation_well_ft"])
    s_pw = np.array(data["pumping_test"].get("drawdown_pumping_well_ft", []))

    r_obs = data["aquifer"]["observation_well_distance_ft"]
    b = data["aquifer"]["b_ft"]

# ======================================================
# AQUIFER TYPE CLASSIFICATION
# ======================================================

    # --------------------------------------------------
    # Analytical Solutions
    # --------------------------------------------------
    print("\n=== ANALYTICAL SOLUTIONS ===")

    theis = theis_fit(t, s_obs, r_obs, Q_cfs)
    print(f"Theis: T={theis['T']:.3f}, S={theis['S']:.3e}")

    cj = cooper_jacob_fit(t, s_obs, r_obs, Q_cfs)
    print(f"Cooper-Jacob: T={cj['T']:.3f}, S={cj['S']:.3e}")

    neuman = neuman_fit(t, s_obs, r_obs, b, Q_cfs)
    print(f"Neuman: T={neuman['T']:.3f}, Sy={neuman['Sy']:.3f}")

    recovery = recovery_fit(
        np.array(data["recovery_test"]["recovery_time_min"]),
        np.array(data["recovery_test"]["recovery_drawdown_ft"]),
        Q_cfs
    )
    print(f"Recovery: T={recovery['T']:.3f}")


    # --------------------------------------------------
    # Recharge Estimate
    # --------------------------------------------------
    annual_precip_in = data["recharge"]["annual_precip_in"]
    infil_frac = data["recharge"]["infiltration_fraction"]

    recharge_gpd_ac = annual_precip_in * infil_frac * 27154
    print(f"\nRecharge Estimate: {recharge_gpd_ac:.2f} gpd/acre")


    # --------------------------------------------------
    # Calibration
    # --------------------------------------------------
    print("\n=== CALIBRATION ===")

    cal = calibrate_parameters(
        t_min=t,
        s_obs=s_obs,
        Q_cfs=Q_cfs,
        r_obs=r_obs,
        model_func=lambda tt, Q, T, Sy, r: theis_s(tt * 60, Q, T / 86400.0, Sy, r),
        T0=cj["T"],
        Sy0=max(min(neuman["Sy"], 0.3), 1e-5),
        bounds={"T": (1, 100), "Sy": (1e-5, 0.1)}
    )

    if not cal["success"]:
        raise RuntimeError(f"Calibration failed: {cal['message']}")

    T_cal = cal["T"]
    Sy_cal = cal["Sy"]

    print(f"Calibrated: T={T_cal:.3f}, Sy={Sy_cal:.3f}")

    # --------------------------------------------------
    # WELL DESIGN & COST MODULES
    # --------------------------------------------------
    print("\n=== WELL DESIGN SUMMARY ===")

    well_design = design_well(
        Q_gpm=Q_gpm,
        T=T_cal,
        Sy=Sy_cal,
        b=b,
        allowable_velocity=0.1,
        user_diameter_in=data.get("well_design", {}).get("diameter_override_in"),
        user_screen_length_ft=data.get("well_design", {}).get("screen_length_override_ft")
    )

    D10 = data.get("aquifer", {}).get("D10_mm", 0.20)
    D50 = data.get("aquifer", {}).get("D50_mm", 0.35)
    gravel_pack = design_gravel_pack(
        aquifer_D10_mm=D10,
        aquifer_D50_mm=D50,
        screen_slot_in=well_design["slot_size_in"],
        desired_thickness_in=data.get("well_design", {}).get("gravel_pack_thickness_in", 4.0)
    )

    develop = estimate_well_development_time(
        screen_length_ft=well_design["screen_length_ft"],
        diameter_in=well_design["diameter_in_final"]
    )

    pump = pump_selection(
        Q_gpm=Q_gpm,
        pumping_level_ft=data["pumping_test"].get("pumping_level_ft", 80),
        discharge_elev_ft=data["pumping_test"].get("discharge_elev_ft", 120)
    )

    pump_energy = pump_energy_cost(
        Q_gpm=Q_gpm,
        HP=pump["HP_recommended"],
        hours_per_day=data.get("operation", {}).get("hours_per_day", 10),
        electricity_rate_per_kWh=data.get("operation", {}).get("electric_rate", 0.12)
    )

    well_cost = estimate_well_cost(
        diameter_in=well_design["diameter_in_final"],
        depth_ft=data.get("well_design", {}).get("total_depth_ft", 120),
        screen_length_ft=well_design["screen_length_ft"]
    )

    os.makedirs("report", exist_ok=True)
    diagram_path = make_well_diagram(
        diameter_in=well_design["diameter_in_final"],
        screen_length_ft=well_design["screen_length_ft"],
        gravel_thickness_ft=gravel_pack["thickness_ft"],
        outfile="report/well_diagram.png"
    )

    print(well_design)
    print(gravel_pack)
    print(develop)
    print(pump)
    print(pump_energy)
    print(well_cost)

    # --------------------------------------------------
    # WELL DESIGN RECOMMENDATION
    # --------------------------------------------------
    well_design = design_well(
        Q_gpm=Q_gpm,
        T=T_cal,
        Sy=Sy_cal,
        b=b,
        allowable_velocity=0.1,            # Ten States limit
        user_diameter_in=data.get("well_design", {}).get("diameter_override_in"),
        user_screen_length_ft=data.get("well_design", {}).get("screen_length_override_ft")
    )

    print("\n=== WELL DESIGN RECOMMENDATION ===")
    print("Recommended Diameter:", well_design["diameter_in_recommended"], "in")
    print("Final Diameter Used:", well_design["diameter_in_final"], "in")
    print("Recommended Screen Length:", well_design["screen_length_ft"], "ft")


    # --------------------------------------------------
    # MULTI-WELL INTERFERENCE MODELING (OPTIONAL)
    # --------------------------------------------------
    interference_summary = None
    if "wells" in data:
        print("\n=== MULTI-WELL INTERFERENCE MODEL ===")

        wells = data["wells"]   # user-defined list in JSON

        times = np.linspace(1, 1440, 200)   # 24-hr simulation
        x_obs = r_obs
        y_obs = 0.0

        dd_multi = multiwell_timeseries(
            wells=wells,
            T=T_cal,
            S=theis["S"],
            x_obs=x_obs,
            y_obs=y_obs,
            times_min=times
        )

        print("Peak interference drawdown:", max(dd_multi))
        interference_summary = {
            "times_min": times.tolist(),
            "drawdown_ft": dd_multi.tolist(),
            "peak_drawdown_ft": float(np.max(dd_multi)),
            "observation_distance_ft": r_obs,
            "wells": wells
        }
    else:
        dd_multi = None

    # --------------------------------------------------
    # 72-HOUR SUSTAINED PUMP TEST SIMULATION
    # --------------------------------------------------
    print("\n=== 72-HOUR SUSTAINED PUMP TEST ===")

    times_72, dd_72 = simulate_72hr_test(
        Q_cfs=Q_cfs,
        T=T_cal,
        S=theis["S"],
        r=r_obs,
        dt_min=5,
        pump_on=True,
        recovery=True
    )

    print("Max 72-hr drawdown:", float(np.max(dd_72)))
    print("Recovery after shutoff:", float(dd_72[-1]))

    pump72_summary = {
        "times_min": times_72.tolist(),
        "drawdown_ft": dd_72.tolist(),
        "max_drawdown_ft": float(np.max(dd_72)),
        "end_value_ft": float(dd_72[-1])
    }

    # --------------------------------------------------
    # FEM MODEL
    # --------------------------------------------------
    print("\n=== RUNNING 2D FEM MODEL ===")

    fd = run_fd2d_model(Q=Q_cfs, T=T_cal, Sy=Sy_cal)

    pump_loc = fd["pump_location"]
    cells_offset = max(1, int(round(r_obs / fd["dx"])))
    obs_col = min(fd["nx"] - 1, pump_loc[0] + cells_offset)
    obs_loc = (obs_col, pump_loc[1])

    plot_drawdown_contours(fd["h"], fd["dx"], fd["dy"], pump_loc, obs_loc)
    print("Drawdown contours saved: report/drawdown_contours.png")


    # --------------------------------------------------
    # WHP ZONES
    # --------------------------------------------------
    print("\n=== WELLHEAD PROTECTION ZONES ===")

    whp = compute_whp_zones(
        fd["h"], fd["dx"], fd["dy"],
        Q_cfs, T_cal, Sy_cal
    )

    print("WHP Zones:", whp)


    # --------------------------------------------------
    # KDOW SWA-2 FORM
    # --------------------------------------------------
    fill_swa2_form(
        results={"T": T_cal, "Sy": Sy_cal, "S": theis["S"], "yield_gpm": Q_gpm},
        inputs=data
    )
    print("KDOW SWA-2 form generated.")

    # --------------------------------------------------
    # Aquifer Classification
    # --------------------------------------------------
    aquifer_class = classify_aquifer(
        T=T_cal,
        S=theis["S"],
        Sy=Sy_cal
    )

    print("\n=== AQUIFER CLASSIFICATION ===")
    print("Aquifer Type:", aquifer_class["type"])
    print("Rationale:", aquifer_class["rationale"])
    print("Note:", aquifer_class["engineering_note"])




    # --------------------------------------------------
    # DYNAMIC WORD REPORT
    # --------------------------------------------------
    print("\n=== GENERATING DYNAMIC REPORT ===")

    results = {
        "inputs": data,
        "theis": theis,
        "cooper_jacob": cj,
        "neuman": neuman,
        "recovery": recovery,
        "calibrated": {"T": T_cal, "Sy": Sy_cal},
        "recharge_gpd": recharge_gpd_ac,
        "fem": fd,
        "whp": whp,
        "interference": interference_summary,
        "pump72": pump72_summary,
        "well_design": {
            "design": well_design,
            "gravel_pack": gravel_pack,
            "development": develop,
            "pump": pump,
            "pump_energy": pump_energy,
            "well_cost": well_cost,
            "diagram": diagram_path
        }
    }

    make_dynamic_report(results)
    print("\nCOMPLETE - Dynamic report generated: report/aquifer_dynamic_report.docx\n")



# ======================================================
# ENTRY POINT
# ======================================================
if __name__ == "__main__":
    main()
