import numpy as np
import math
from .theis import theis_W



def simulate_72hr_test(Q_cfs, T, S, r, dt_min=5, pump_on=True, recovery=False):
    """
    Simulates a 72-hour pumping + recovery test using the Theis solution.
    """
    T_hours = 72     # pumping portion
    R_hours = 48     # recovery portion
    t_total = (T_hours + R_hours) * 60

    times = np.arange(dt_min, t_total, dt_min)
    s = []

    for t in times:
        t_sec = t * 60

        if recovery and t > T_hours * 60:
            # RECOVERY PHASE
            t_pump = T_hours * 60
            t_rec = t_sec - t_pump
            u = (r**2 * S) / (4 * T * t_rec)

            # Jacob straight-line recovery solution
            s_rec = (Q_cfs / (4 * math.pi * T)) * theis_W(u)
            s.append(-s_rec)   # heads rising (negative drawdown)
        else:
            # PUMPING PHASE
            u = (r**2 * S) / (4 * T * t_sec)
            s_pump = (Q_cfs / (4 * math.pi * T)) * theis_W(u)
            s.append(s_pump)

    return times, np.array(s)

import base64
import io
import numpy as np
import matplotlib.pyplot as plt

def run_72hr_test(transient_solver, grid, boundaries, T, Sy, pumping_well_id, Q_cfs):
    """
    Creates a 72-hour pump test using the transient solver:
       • 72 hr pumping
       • 24 hr recovery
    """

    # Build special stress periods
    stress_periods = [
        {
            "duration_hours": 72,
            "time_steps": 72,
            "pumping": {pumping_well_id: Q_cfs},
            "recharge_in_per_day": 0.0
        },
        {
            "duration_hours": 24,
            "time_steps": 24,
            "pumping": {pumping_well_id: 0.0},
            "recharge_in_per_day": 0.0
        }
    ]

    # Initial head (flat)
    h0 = np.ones(grid.shape) * grid.initial_head

    # Run transient model
    heads = transient_solver.run(stress_periods, h0)

    # Extract pumping well time series
    pwx, pwy = grid.pump_location
    pump_ts = heads[:, pwy, pwx]

    max_drawdown = float(heads[0, pwy, pwx] - np.min(pump_ts))
    final_recovery = float(pump_ts[-1] - pump_ts[72])  # recovery after shutoff

    # Stability: slope of last 6 hours
    slope = np.mean(np.gradient(pump_ts[60:72]))
    stable = abs(slope) < 0.02

    recommended_yield_gpm = None
    if not stable:
        recommended_yield_gpm = float((Q_cfs * 0.75) * 448.831)

    # Create plots
    plots = {}

    # Drawdown curve
    fig, ax = plt.subplots()
    ax.plot(np.arange(73), pump_ts[:73], lw=2)
    ax.set_title("72-Hour Drawdown Curve")
    ax.set_xlabel("Time (hr)")
    ax.set_ylabel("Head (ft)")
    ax.grid()

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    plots["pump72_drawdown"] = base64.b64encode(buf.getvalue()).decode()

    # Recovery curve
    fig, ax = plt.subplots()
    ax.plot(np.arange(24), pump_ts[72:], lw=2, color="green")
    ax.set_title("24-Hour Recovery Curve")
    ax.set_xlabel("Time After Pumping (hr)")
    ax.set_ylabel("Head (ft)")
    ax.grid()

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    plots["pump72_recovery"] = base64.b64encode(buf.getvalue()).decode()

    return {
        "max_drawdown_ft": max_drawdown,
        "final_recovery_ft": final_recovery,
        "stable": stable,
        "recommended_yield_gpm": recommended_yield_gpm,
        "plots": plots
    }
