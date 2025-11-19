import base64
import io
import matplotlib.pyplot as plt
import numpy as np

def make_hydrograph_plot(times_hr, heads_3d, pump_loc, obs_locs):
    """
    Produces hydrograph plots for:
      • Pumping well (time-series head)
      • Observation wells (time-series head)
    Returns PNG base64 images for frontend/PDF.
    """
    images = {}

    # Extract pumping well time series
    pw_x, pw_y = pump_loc
    pump_ts = heads_3d[:, pw_y, pw_x]

    for label, ts in [("pumping_well", pump_ts)]:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(times_hr, ts, lw=2)
        ax.set_xlabel("Time (hr)")
        ax.set_ylabel("Head (ft)")
        ax.set_title(f"Hydrograph – {label.replace('_', ' ').title()}")
        ax.grid()

        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        images[label] = base64.b64encode(buf.getvalue()).decode()
    
    # Observation wells
    for i, obs in enumerate(obs_locs):
        ox, oy = obs
        obs_ts = heads_3d[:, oy, ox]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(times_hr, obs_ts, lw=2, color="green")
        ax.set_xlabel("Time (hr)")
        ax.set_ylabel("Head (ft)")
        ax.set_title(f"Hydrograph – Observation Well {i+1}")
        ax.grid()

        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        images[f"observation_{i+1}"] = base64.b64encode(buf.getvalue()).decode()

    return images
