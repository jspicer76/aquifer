# backend/src/models/boundaries.py

import numpy as np

class BoundaryProcessor:

    def __init__(self, dx, dy, origin_latlng, transform_func):
        """
        dx, dy: grid resolution in ft
        origin_latlng: reference coordinate for projection
        transform_func(lat, lng) → (x_ft, y_ft)
        """
        self.dx = dx
        self.dy = dy
        self.origin = origin_latlng
        self.transform = transform_func   # you already have this for maps

    # -------------------------------------------------------
    # Convert list of lat/lng pairs → grid indices
    # -------------------------------------------------------
    def project_polyline(self, coords):
        grid = []
        for (lat, lng) in coords:
            x, y = self.transform(lat, lng)
            i = int(x / self.dx)
            j = int(y / self.dy)
            grid.append((i, j))
        return grid

    def project_polygon(self, coords):
        return self.project_polyline(coords)

    # -------------------------------------------------------
    # Prepare all boundary types for FEM
    # -------------------------------------------------------
    def process(self, boundaries):
        """
        boundaries = {
          'constant_head': [{points, head}, ...]
          'no_flow':       [{points}, ...]
          'recharge_zones':[{polygon, rate}, ...]
          'general_head':  [{points, head, cond}, ...]
        }
        """

        out = dict(
            constant_head=[],
            no_flow=[],
            recharge_zones=[],
            general_head=[]
        )

        # Constant Head → Dirichlet
        for b in boundaries.get("constant_head", []):
            pts = self.project_polyline(b["points"])
            out["constant_head"].append({
                "nodes": pts,
                "head": b["head"]
            })

        # No-Flow → Neumann (zero flux)
        for b in boundaries.get("no_flow", []):
            pts = self.project_polyline(b["points"])
            out["no_flow"].append({
                "nodes": pts
            })

        # Recharge zones → polygons + rate
        for b in boundaries.get("recharge_zones", []):
            poly = self.project_polygon(b["polygon"])
            out["recharge_zones"].append({
                "polygon": poly,
                "rate": b["rate"]
            })

        # GHB → C(h0 - h)
        for b in boundaries.get("general_head", []):
            pts = self.project_polyline(b["points"])
            out["general_head"].append({
                "nodes": pts,
                "head": b["head"],
                "cond": b["cond"]
            })

        return out
