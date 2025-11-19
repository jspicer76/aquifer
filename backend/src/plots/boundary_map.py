import os
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np


BoundaryDict = Dict[str, List[Dict]]


def _is_latlng_pair(pair: Sequence[float]) -> bool:
    if len(pair) != 2:
        return False
    lat, lng = pair
    return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0


def _points_look_like_latlng(points: Sequence[Sequence[float]]) -> bool:
    return all(_is_latlng_pair(pt) for pt in points if len(pt) == 2)


def _normalize_points(
    points: Sequence[Sequence[float]],
    lat_min: float,
    lat_max: float,
    lng_min: float,
    lng_max: float,
    nx: int,
    ny: int,
) -> List[Tuple[float, float]]:
    if not points:
        return []

    lat_span = max(lat_max - lat_min, 1e-6)
    lng_span = max(lng_max - lng_min, 1e-6)

    normalized = []
    for lat, lng in points:
        x = ((lng - lng_min) / lng_span) * max(nx - 1, 1)
        y = ((lat - lat_min) / lat_span) * max(ny - 1, 1)
        normalized.append((x, y))
    return normalized


def _polygon_area_acres(points: Sequence[Tuple[float, float]], dx: float, dy: float) -> Optional[float]:
    if len(points) < 3:
        return None

    coords = [(x * dx, y * dy) for x, y in points]
    area = 0.0
    for (x1, y1), (x2, y2) in zip(coords, coords[1:] + coords[:1]):
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5 / 43560.0


def process_boundary_payload(
    boundaries: Optional[BoundaryDict],
    nx: int,
    ny: int,
    dx: float,
    dy: float,
) -> Optional[BoundaryDict]:
    if not boundaries:
        return None

    processed: BoundaryDict = {
        "constant_head": [],
        "no_flow": [],
        "recharge_zones": [],
        "general_head": []
    }

    all_points: List[Tuple[float, float]] = []
    for key in ("constant_head", "no_flow", "recharge_zones", "general_head"):
        entries = boundaries.get(key, [])
        coord_key = "polygon" if key == "recharge_zones" else "points"
        for entry in entries:
            for pt in entry.get(coord_key, []):
                if isinstance(pt, (list, tuple)) and len(pt) == 2:
                    all_points.append((float(pt[0]), float(pt[1])))

    use_latlng = bool(all_points) and _points_look_like_latlng(all_points)
    if use_latlng:
        lat_min = min(pt[0] for pt in all_points)
        lat_max = max(pt[0] for pt in all_points)
        lng_min = min(pt[1] for pt in all_points)
        lng_max = max(pt[1] for pt in all_points)

        def convert_points(pts):
            return _normalize_points(pts, lat_min, lat_max, lng_min, lng_max, nx, ny)
    else:
        def convert_points(pts):
            return [(float(x), float(y)) for x, y in pts]

    for entry in boundaries.get("constant_head", []):
        pts = convert_points(entry.get("points", []))
        processed["constant_head"].append({
            "head": entry.get("head"),
            "points": pts
        })

    for entry in boundaries.get("no_flow", []):
        pts = convert_points(entry.get("points", []))
        processed["no_flow"].append({
            "points": pts
        })

    for entry in boundaries.get("recharge_zones", []):
        pts = convert_points(entry.get("polygon", []))
        processed["recharge_zones"].append({
            "polygon": pts,
            "rate": entry.get("rate"),
            "area_acres": _polygon_area_acres(pts, dx, dy)
        })

    for entry in boundaries.get("general_head", []):
        pts = convert_points(entry.get("points", []))
        processed["general_head"].append({
            "points": pts,
            "head": entry.get("head"),
            "cond": entry.get("cond")
        })

    if all(len(processed[key]) == 0 for key in processed):
        return None

    return processed


def plot_boundary_map(
    heads: np.ndarray,
    dx: float,
    dy: float,
    boundaries: BoundaryDict,
    outpath: str
):
    if not boundaries:
        return

    os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)

    plt.figure(figsize=(8, 6))
    extent = [0, heads.shape[1], 0, heads.shape[0]]
    plt.imshow(heads, origin="lower", cmap="viridis", extent=extent, aspect="auto")
    plt.colorbar(label="Hydraulic Head (ft)")

    def _plot_lines(entries, color, **kwargs):
        for entry in entries:
            pts = np.array(entry.get("points", []))
            if len(pts) >= 2:
                plt.plot(pts[:, 0], pts[:, 1], color=color, **kwargs)

    _plot_lines(boundaries.get("constant_head", []), "#003f91", linewidth=2)
    _plot_lines(boundaries.get("no_flow", []), "#c1121f", linewidth=2)
    _plot_lines(boundaries.get("general_head", []), "#f77f00", linewidth=2, linestyle="--")

    for entry in boundaries.get("recharge_zones", []):
        pts = np.array(entry.get("polygon", []))
        if len(pts) >= 3:
            plt.fill(pts[:, 0], pts[:, 1], color="#2a9d8f", alpha=0.3)

    plt.title("Boundary Condition Overlay")
    plt.xlabel(f"Distance (cells of {dx:.0f} ft)")
    plt.ylabel(f"Distance (cells of {dy:.0f} ft)")
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()
