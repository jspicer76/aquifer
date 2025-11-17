import numpy as np
import math
from methods.theis import theis_W

# ---------------------------------------------------------
# MULTI-WELL INTERFERENCE (THEIS SUPERPOSITION)
# ---------------------------------------------------------
def multiwell_drawdown(wells, T, S, x, y, t):
    """
    wells = list of dicts:
        {
            "Q": pumping rate (cfs),
            "x": x-location (ft),
            "y": y-location (ft),
            "start": time pump starts (min),
            "stop": time pump stops (min)
        }

    x,y = observation point (ft)
    t   = time (min)
    """

    total_s = 0.0

    for w in wells:
        if t < w["start"]:
            continue
        if w["stop"] is not None and t > w["stop"]:
            continue

        t_eff = (t - w["start"]) * 60.0  # Convert minutes → seconds
        if t_eff <= 0:
            continue

        dx = x - w["x"]
        dy = y - w["y"]
        r = math.sqrt(dx*dx + dy*dy)

        u = (r**2 * S) / (4 * T * t_eff)
        s = (w["Q"] / (4 * math.pi * T)) * theis_W(u)
        total_s += s

    return total_s


# ---------------------------------------------------------
# GENERATE TIME-SERIES FOR OBSERVATION POINT
# ---------------------------------------------------------
def multiwell_timeseries(wells, T, S, x_obs, y_obs, times_min):
    dd = []
    for t in times_min:
        dd.append(multiwell_drawdown(wells, T, S, x_obs, y_obs, t))
    return np.array(dd)
