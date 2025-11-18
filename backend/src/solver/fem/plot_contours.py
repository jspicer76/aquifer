import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless backend for non-GUI environments
import matplotlib.pyplot as plt

def plot_drawdown_contours(h, dx, dy, pump_location, obs_location):
    ny, nx = h.shape
    x = np.arange(0, nx*dx, dx)
    y = np.arange(0, ny*dy, dy)
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(figsize=(10, 8))
    cs = ax.contour(X, Y, 100 - h, levels=20, linewidths=1.2)
    ax.clabel(cs, inline=True, fontsize=10)

    ax.plot(pump_location[0]*dx, pump_location[1]*dy, 'ro', label="Pumping Well")
    ax.plot(obs_location[0]*dx, obs_location[1]*dy, 'bo', label="Observation Well")

    ax.set_title("Drawdown Contours (ft)")
    ax.set_xlabel("Distance (ft)")
    ax.set_ylabel("Distance (ft)")
    ax.legend()
    plt.savefig("report/drawdown_contours.png", dpi=300)
    plt.close()
