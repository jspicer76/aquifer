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
    # backend/src/solver/fem/fd2d_solver.py

    from .boundary_assembly import BoundaryAssembler
    from backend.src.models.boundaries import BoundaryProcessor

    def run_fd2d_model(Q, T, Sy, boundaries=None, **kwargs):

        # --- existing FD assembly ---
        A, b = assemble_matrix(T, Sy, Q, ...)

        assembler = BoundaryAssembler(A, b, dx, dy)
        assembler.set_grid_shape(nx, ny)

        # ---------------------------------------
        # Apply boundaries if provided
        # ---------------------------------------
        if boundaries:

            # Convert lat/lng → grid indices
            bp = BoundaryProcessor(dx, dy, origin_latlng, geo_to_ft)
            bc = bp.process(boundaries)

            for b in bc["constant_head"]:
                assembler.apply_constant_head(b["nodes"], b["head"])

            for b in bc["no_flow"]:
                assembler.apply_no_flow(b["nodes"])

            for b in bc["recharge_zones"]:
                assembler.apply_recharge(b["polygon"], b["rate"])

            for b in bc["general_head"]:
                assembler.apply_ghb(b["nodes"], b["head"], b["cond"])

        # Solve system
        h = np.linalg.solve(assembler.A, assembler.b)

        return h.reshape((ny, nx))
