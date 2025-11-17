import numpy as np
from scipy.optimize import least_squares


def calibrate_parameters(
        t_min,
        s_obs,
        Q_cfs,
        r_obs,
        model_func,
        T0,
        Sy0,
        bounds
    ):
    """
    Universal calibration engine using log-space optimization for stability.
    Fits transmissivity (T) and specific yield/storativity (Sy) to observations.
    """

    t_sec = np.array(t_min) * 60.0
    s_obs = np.array(s_obs)

    Tmin, Tmax = bounds["T"]
    Symin, Symax = bounds["Sy"]

    Tmin = max(Tmin, 1e-12)
    Symin = max(Symin, 1e-12)

    T0_clipped = min(max(T0, Tmin * 1.001), Tmax / 1.001)
    Sy0_clipped = min(max(Sy0, Symin * 1.001), Symax / 1.001)

    log_T0 = np.log10(T0_clipped)
    log_Sy0 = np.log10(Sy0_clipped)

    lower = [np.log10(Tmin), np.log10(Symin)]
    upper = [np.log10(Tmax), np.log10(Symax)]

    scale = np.max(s_obs) if np.max(s_obs) > 0 else 1.0
    weights = 1.0 / (np.power(t_sec + 1.0, 1.5))

    def residuals(log_params):
        log_T, log_Sy = log_params
        T = 10 ** log_T
        Sy = 10 ** log_Sy
        s_model = np.array([
            model_func(tt, Q_cfs, T, Sy, r_obs)
            for tt in t_sec
        ])
        return ((s_model - s_obs) * weights) / scale

    result = least_squares(
        residuals,
        x0=[log_T0, log_Sy0],
        bounds=(lower, upper),
        method="trf",
        max_nfev=2000
    )

    log_T_fit, log_Sy_fit = result.x
    T_fit = 10 ** log_T_fit
    Sy_fit = 10 ** log_Sy_fit

    return {
        "T": float(T_fit),
        "Sy": float(Sy_fit),
        "success": bool(result.success),
        "message": result.message
    }
