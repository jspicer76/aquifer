import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

class TransientSolver:
    """
    Full transient MODFLOW-style solver.
    Supports:
        - Stress periods
        - Time steps
        - Time-varying pumping
        - Time-varying recharge
        - Constant-head & river boundaries
        - No-flow boundaries
        - Storage term Sy * dh/dt
    """

    def __init__(self, grid, boundaries, T, Sy):
        self.grid = grid
        self.boundaries = boundaries
        self.T = T
        self.Sy = Sy

    # ---------- helper ----------
    def implicit_step(self, A, RHS, h_old, dt):
        n = A.shape[0]
        I = csr_matrix(np.eye(n))

        # Transient coefficient
        A_t = A + (self.Sy / dt) * I
        RHS_t = RHS + (self.Sy / dt) * h_old

        h_new = spsolve(A_t, RHS_t)
        return h_new

    # ---------- main run ----------
    def run(self, stress_periods, h0):
        heads = []
        h = h0.copy()

        for sp in stress_periods:
            dt = sp["duration_hours"] / sp["time_steps"]
            dt_sec = dt * 3600

            for _ in range(sp["time_steps"]):

                # Build FEM matrix for this timestep
                A, RHS = self.grid.build_matrix(
                    T=self.T,
                    pumping=sp["pumping"],
                    recharge=sp["recharge_in_per_day"],
                    boundaries=self.boundaries,
                )

                # Apply transient step
                h_new = self.implicit_step(A, RHS, h, dt_sec)
                heads.append(h_new.reshape(self.grid.shape))

                h = h_new.copy()

        return np.array(heads)
