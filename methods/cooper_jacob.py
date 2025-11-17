import numpy as np
import math

def cooper_jacob_fit(t, s, Q, r):
    logt = np.log10(t)
    slope, intercept = np.polyfit(logt, s, 1)

    T = 2.303 * Q / (4 * math.pi * slope)
    t0 = 10 ** (-intercept / slope)
    S = (2.25 * T * t0) / (r**2)

    return {"T": T, "S": S, "slope": slope, "t0": t0}
