import matplotlib.pyplot as plt
import numpy as np

def plot_boundary_map(h, dx, dy, boundaries, outpath):
    plt.figure(figsize=(8,6))
    plt.imshow(h, origin="lower", cmap="viridis")
    plt.colorbar(label="Hydraulic Head (ft)")

    # Plot Constant Head
    for b in boundaries.get("constant_head", []):
        pts = np.array(b["nodes"])
        plt.plot(pts[:,0], pts[:,1], color="#003f91", linewidth=2)

    # Plot No-Flow
    for b in boundaries.get("no_flow", []):
        pts = np.array(b["nodes"])
        plt.plot(pts[:,0], pts[:,1], color="#c1121f", linewidth=2)

    # Plot Recharge Zones
    for b in boundaries.get("recharge_zones", []):
        poly = np.array(b["polygon"])
        plt.fill(poly[:,0], poly[:,1], color="#2a9d8f", alpha=0.3)

    # Plot GHB
    for b in boundaries.get("general_head", []):
        pts = np.array(b["nodes"])
        plt.plot(pts[:,0], pts[:,1], color="#f77f00", linewidth=2, linestyle="--")

    plt.title("Boundary Condition Overlay")
    plt.savefig(outpath, dpi=120)
    plt.close()
