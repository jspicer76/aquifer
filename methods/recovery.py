import numpy as np

def recovery_fit(t_min, s_rec, Q_cfs, t_pump=None):
    """
    Theis recovery method (straight-line fit).
    s = (Q / 4πT) * ln(t / t')
    t_min : array of recovery times (minutes)
    s_rec : array of recovery drawdowns (ft)
    Q_cfs : pumping rate in cfs
    t_pump : total pumping time in minutes (defaults to last pumping t)
    """

    t_sec = np.array(t_min) * 60.0
    s_rec = np.array(s_rec)

    # Default: t' = last pumping time
    if t_pump is None:
        t_pump = t_sec.max()

    # Compute ln(t/t')
    ln_term = np.log(t_sec / t_pump)

    # Linear regression: s = m * ln(t/t')
    m = np.sum(ln_term * s_rec) / np.sum(ln_term ** 2)

    # T = Q / (4πm)
    T = Q_cfs / (4 * np.pi * m)

    return {
        "T": float(T),
        "slope": float(m),
        "t_pump_sec": float(t_pump)
    }
