# backend/src/solver/fem/boundary_assembly.py

import numpy as np

class BoundaryAssembler:

    def __init__(self, A, b, dx, dy):
        self.A = A
        self.b = b
        self.dx = dx
        self.dy = dy

    # --------------------------------------
    # Apply Constant-Head (Dirichlet)
    # --------------------------------------
    def apply_constant_head(self, nodes, head):
        for (i, j) in nodes:
            idx = self.to_idx(i, j)
            self.A[idx, :] = 0.0
            self.A[idx, idx] = 1.0
            self.b[idx] = head

    # --------------------------------------
    # Apply No-Flow (Neumann = 0)
    # → Implemented by enforcing zero gradient across boundary
    # --------------------------------------
    def apply_no_flow(self, nodes):
        # For FD model:
        # Zero-gradient = h(boundary) = h(interior cell)
        for (i, j) in nodes:
            idx = self.to_idx(i, j)

            # Replace equation with "h(i,j) - h(i-1,j) = 0"
            self.A[idx, :] = 0.0
            interior = self.to_idx(max(i-1, 0), j)
            self.A[idx, idx] = 1.0
            self.A[idx, interior] = -1.0
            self.b[idx] = 0.0

    # --------------------------------------
    # Recharge Zone → source term addition
    # --------------------------------------
    def apply_recharge(self, polygon, rate):
        # rasterization: find all grid cells inside polygon
        from matplotlib.path import Path

        poly_arr = np.array(polygon)
        path = Path(poly_arr)

        nx, ny = self.grid_shape

        for i in range(nx):
            for j in range(ny):
                # cell center
                x = i * self.dx
                y = j * self.dy
                if path.contains_points([(x, y)])[0]:
                    idx = self.to_idx(i, j)
                    recharge_cfs = rate / 7.48 / 86400  # convert gpd/acre → ft³/s/ft²
                    self.b[idx] += recharge_cfs

    # --------------------------------------
    # GHB → C(h0 - h) term
    # --------------------------------------
    def apply_ghb(self, nodes, head, cond):
        for (i, j) in nodes:
            idx = self.to_idx(i, j)

            # Add conductance term: C * h0 → RHS
            self.b[idx] += cond * head

            # Add C term to diagonal
            self.A[idx, idx] += -cond

    # --------------------------------------
    # Flatten (i,j) → 1D index
    # --------------------------------------
    def to_idx(self, i, j):
        nx, ny = self.grid_shape
        return j * nx + i

    # Must be set externally after grid created
    def set_grid_shape(self, nx, ny):
        self.grid_shape = (nx, ny)
