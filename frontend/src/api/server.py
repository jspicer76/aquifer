from fastapi import APIRouter
from solver.fem.whp_geojson import whp_to_geojson

router = APIRouter()

@router.post("/whp_geojson")
def whp_geojson(payload: dict):
    wells = payload["wells"]
    aquifer = payload["aquifer"]

    result = whp_to_geojson(wells, aquifer)
    return result
