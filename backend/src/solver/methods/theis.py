import math
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import expn


def theis_W(u):
    """Stable evaluation of the Theis well function."""
    u = np.maximum(u, 1e-12)
    return expn(1, u)


def theis_s(t, Q, T, S, r):
    """
    Compute drawdown using the Theis solution.

    Parameters
    ----------
    t : float
        Time since pumping started (seconds).
    Q : float
        Pumping rate (ft^3/s).
    T : float
        Transmissivity (ft^2/s).
    S : float
        Storativity (dimensionless).
    r : float
        Observation radius (ft).
    """
    u = (r * r * S) / (4.0 * T * t)
    return (Q / (4.0 * math.pi * T)) * theis_W(u)


def theis_fit(t_min, s_obs, r, Q_cfs):
    """
    Fit the Theis solution to observed drawdown data.

    Returns
    -------
    dict with T (ft^2/day), S, and s_pred arrays for plotting.
    """
    t_sec = t_min * 60.0

    # Initial guesses expressed in ft^2/s
    T0 = 200.0 / 86400.0
    S0 = 5e-3

    def model(tsec, T, S):
        return np.array([theis_s(tt, Q_cfs, T, S, r) for tt in tsec])

    sigma = np.maximum(s_obs, 0.05)

    popt, _ = curve_fit(
        model,
        t_sec,
        s_obs,
        p0=[T0, S0],
        bounds=([1e-10, 1e-6], [1e-1, 5e-1]),
        sigma=sigma,
        absolute_sigma=False,
        maxfev=20000,
    )

    T_fit, S_fit = popt
    T_ft_day = T_fit * 86400.0
    s_pred = model(t_sec, T_fit, S_fit)

    return {"T": T_ft_day, "S": S_fit, "s_pred": s_pred}
