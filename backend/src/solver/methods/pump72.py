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
