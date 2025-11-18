import numpy as np

from .boundaries import (
    BoundaryCollection,
    ConstantHeadBoundary,
    NoFlowBoundary,
    SpecifiedFluxBoundary,
    RiverBoundary,
    RechargeBoundary,
)


def run_fd2d_model(
    Q,
    T,
    Sy,
    Lx=2000,
    Ly=2000,
    dx=20,
    dy=20,
    boundaries: BoundaryCollection = None,
    max_iters=600
):
    """
    2-D Finite Difference Groundwater Flow Model
    -------------------------------------------
    Supports:
        • Pumping well (center of domain)
        • Constant-head boundaries (Dirichlet)
        • No-flow boundaries (Neumann)
        • River boundaries (Cauchy)
        • Specified flux boundaries
        • Recharge boundaries (areal)
    """

    nx = int(Lx / dx)
    ny = int(Ly / dy)

    # Base initial head (can adjust later if needed)
    h = np.ones((ny, nx)) * 100.0

    # Pumping well at center
    pump_i = ny // 2
    pump_j = nx // 2

    # Default: no boundaries
    if boundaries is None:
        boundaries = BoundaryCollection()

    # ----------------------------------------------------------
    # MAIN FINITE DIFFERENCE LOOP
    # ----------------------------------------------------------
    for _ in range(max_iters):
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):

                # ===============================
                # NO-FLOW (Neumann = 0)
                # ===============================
                is_noflow = any((i, j) in b.cells for b in boundaries.no_flow)
                if is_noflow:
                    continue

                # ===============================
                # CONSTANT HEAD (Dirichlet)
                # ===============================
                ch = [b for b in boundaries.constant_head if (i, j) in b.cells]
                if ch:
                    h[i, j] = ch[0].head_ft
                    continue

                # ===============================
                # RIVER BOUNDARY (Cauchy)
                # Q = C (h_riv − h_cell)
                # ===============================
                rv = [b for b in boundaries.river if (i, j) in b.cells]
                if rv:
                    b = rv[0]
                    hr = b.river_stage_ft
                    C = b.conductance

                    # Weighted average update
                    h[i, j] = (
                        C * hr +
                        (T / dx**2) * (h[i+1, j] + h[i-1, j] + h[i, j+1] + h[i, j-1])
                    ) / (C + 4 * T / dx**2)
                    continue

                # ===============================
                # NORMAL FD UPDATE
                # ===============================
                h[i, j] = 0.25 * (
                    h[i + 1, j] +
                    h[i - 1, j] +
                    h[i, j + 1] +
                    h[i, j - 1]
                )

        # ------------------------------------------------------
        # APPLY PUMPING (sink term at center node)
        # Q is in ft³/s — convert to ft³/day
        # ------------------------------------------------------
        Q_day = Q * 86400
        h[pump_i, pump_j] -= Q_day / (T * dx * dy)

        # ------------------------------------------------------
        # RECHARGE (areal) — adds water
        # ------------------------------------------------------
        for b in boundaries.recharge:
            for (ri, rj) in b.cells:
                h[ri, rj] += b.recharge / Sy

        # ------------------------------------------------------
        # SPECIFIED FLUX boundaries
        # q = flux (ft³/day)
        # head change = q / (T)
        # ------------------------------------------------------
        for b in boundaries.specified_flux:
            for (fi, fj) in b.cells:
                h[fi, fj] += b.flux / (T * dx * dy)

    # -------------------------------
    # RETURN MODEL RESULTS
    # -------------------------------
    return {
        "h": h,
        "dx": dx,
        "dy": dy,
        "pump_location": (pump_j, pump_i),
        "nx": nx,
        "ny": ny
    }
