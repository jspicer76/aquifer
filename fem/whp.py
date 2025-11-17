import numpy as np

def compute_whp_zones(h, dx, dy, Q_cfs, T, Sy):
    """
    Compute Wellhead Protection Zones using KDOW-approved
    time-of-travel radii: 50-day, 5-year, 10-year.
    Uses analytical radius R = sqrt( (2 * T * Δh * t) / Sy ).
    """

    # Δh: drawdown at well relative to outer boundary
    h0 = np.nanmax(h)
    hw = np.nanmin(h)
    dh = max(h0 - hw, 0.1)  # prevent divide by zero

    # KDOW compliance times in seconds
    t_50day = 50 * 24 * 3600
    t_5yr   = 5 * 365 * 24 * 3600
    t_10yr  = 10 * 365 * 24 * 3600

    def radius(t_sec):
        R = np.sqrt((2 * T * dh * t_sec) / Sy)
        return float(max(R, 10.0))

    zone1 = radius(t_50day)
    zone2 = radius(t_5yr)
    zone3 = radius(t_10yr)

    return {
        "zone1_radius_ft": zone1,
        "zone2_radius_ft": zone2,
        "zone3_radius_ft": zone3,
        "dh_used": dh
    }
