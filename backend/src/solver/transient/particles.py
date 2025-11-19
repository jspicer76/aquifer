import numpy as np
import base64, io
import matplotlib.pyplot as plt

class ParticleTracker:

    def __init__(self, grid, T, Sy):
        self.grid = grid
        self.T = T
        self.Sy = Sy

    def compute_velocity(self, heads_t):
        """Compute vx, vy velocity fields from head gradients."""
        dhdx = np.gradient(heads_t, self.grid.dx, axis=1)
        dhdy = np.gradient(heads_t, self.grid.dy, axis=0)

        vx = -self.T / self.Sy * dhdx
        vy = -self.T / self.Sy * dhdy
        return vx, vy

    def run_particle(self, x0, y0, heads_3d, dt_hr):
        """Track one particle through transient model."""
        x, y = x0, y0
        path = [(x, y)]
        captured = False
        capture_time = None

        dt = dt_hr * 3600

        for t in range(len(heads_3d) - 1):
            vx, vy = self.compute_velocity(heads_3d[t])

            # nearest-cell velocity
            ix = int(round(x / self.grid.dx))
            iy = int(round(y / self.grid.dy))

            if ix < 0 or iy < 0 or ix >= self.grid.nx or iy >= self.grid.ny:
                break

            vxt = vx[iy, ix]
            vyt = vy[iy, ix]

            # RK2 integration
            x_mid = x + 0.5 * vxt * dt
            y_mid = y + 0.5 * vyt * dt

            ix2 = int(round(x_mid / self.grid.dx))
            iy2 = int(round(y_mid / self.grid.dy))
            if ix2 < 0 or iy2 < 0 or ix2 >= self.grid.nx or iy2 >= self.grid.ny:
                break

            vxt2 = vx[iy2, ix2]
            vyt2 = vy[iy2, ix2]

            x += vxt2 * dt
            y += vyt2 * dt
            path.append((x, y))

            # CAPTURE CHECK
            pwx, pwy = self.grid.pump_location
            cx = pwx * self.grid.dx
            cy = pwy * self.grid.dy

            if (x - cx)**2 + (y - cy)**2 < (0.5**2):  # within 0.5 ft
                captured = True
                capture_time = t * dt_hr
                break

        return {
            "path": path,
            "captured": captured,
            "capture_time_hr": capture_time,
        }

    def batch_particles(self, start_points, heads_3d, dt_hr):
        results = []
        for p in start_points:
            results.append(self.run_particle(p[0], p[1], heads_3d, dt_hr))
        return results
