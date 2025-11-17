import numpy as np

def neuman_fit(t, s, Q, r, b):
    # Fit Sy from late-time slope
    slope, _ = np.polyfit(np.sqrt(t), s, 1)

    Sy = (2 * slope * np.sqrt(np.pi) * r) / Q
    Sy = max(Sy, 0.01)

    # Transmissivity from early-time (proxy)
    early_slope, _ = np.polyfit(np.log10(t[:len(t)//3]), s[:len(t)//3], 1)
    T = Q / (4 * np.pi * early_slope)

    return {"T": T, "Sy": Sy}
