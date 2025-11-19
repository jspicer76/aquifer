import json
from shapely.geometry import Point
from shapely.ops import unary_union

def whp_to_geojson(wells, aquifer):
    # Example TOT radii (ft)
    r1 = 100.0   # 1-year
    r2 = 2000.0  # 5-year
    r3 = 5000.0  # 10-year

    features = []

    for w in wells:
        p = Point(w["lng"], w["lat"])

        zones = [
            ("Zone1", r1),
            ("Zone2", r2),
            ("Zone3", r3)
        ]

        for name, radius in zones:
            circle = p.buffer(radius / 364000.0)  # ft → degrees approx

            features.append({
                "type": "Feature",
                "geometry": json.loads(circle.to_geojson()),
                "properties": {
                    "well_id": w["id"],
                    "zone": name,
                    "radius_ft": radius
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
