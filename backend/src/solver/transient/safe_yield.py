from .pump72 import run_72hr_test

def optimize_safe_yield(transient_solver, grid, boundaries, T, Sy, pumping_well_id,
                        Q_min_cfs, Q_max_cfs, tolerance=0.01):
    """
    Binary-search optimization of safe pumping rate.
    Returns Q_safe_gpm.
    """

    Q_low = Q_min_cfs
    Q_high = Q_max_cfs

    last_good = Q_low

    while (Q_high - Q_low) > tolerance:
        Q_try = 0.5 * (Q_high + Q_low)

        result = run_72hr_test(
            transient_solver=transient_solver,
            grid=grid,
            boundaries=boundaries,
            T=T,
            Sy=Sy,
            pumping_well_id=pumping_well_id,
            Q_cfs=Q_try
        )

        if result["stable"]:
            last_good = Q_try
            Q_low = Q_try
        else:
            Q_high = Q_try

    return {
        "safe_yield_cfs": last_good,
        "safe_yield_gpm": last_good * 448.831
    }
