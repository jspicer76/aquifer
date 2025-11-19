import copy
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..main import load_inputs, main as run_model_pipeline


app = FastAPI(
    title="Aquifer Analysis API",
    version="0.1.0",
    description="HTTP interface for running the aquifer analysis model."
)


class Well(BaseModel):
    id: str = Field(..., min_length=1)
    type: Literal["pumping", "observation"]
    lat: float
    lng: float


class RunModelRequest(BaseModel):
    wells: List[Well] = Field(default_factory=list)
    overrides: Optional[Dict[str, Any]] = None
    generate_report: bool = False


def _merge_payload(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Deep-merge overrides into the base dictionary without mutating either."""
    if not overrides:
        return copy.deepcopy(base)

    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_payload(merged[key], value)
        else:
            merged[key] = value
    return merged


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": _utc_timestamp()}


@app.post("/api/model/run")
def run_model(request: RunModelRequest):
    payload = _merge_payload(load_inputs(), request.overrides)
    if request.wells:
        payload["scenario_wells"] = [well.dict() for well in request.wells]

    try:
        results = run_model_pipeline(payload, generate_report=request.generate_report)
    except Exception as exc:  # pragma: no cover - surfaced to client
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    aquifer_class = results.get("aquifer_class") or {}
    calibrated = results.get("calibrated") or {}
    interference = results.get("interference") or {}
    pump72 = results.get("pump72") or {}

    summary = {
        "aquifer_type": aquifer_class.get("type"),
        "calibrated_T": calibrated.get("T"),
        "calibrated_Sy": calibrated.get("Sy"),
        "peak_drawdown_ft": interference.get("peak_drawdown_ft"),
        "max_72hr_drawdown_ft": pump72.get("max_drawdown_ft"),
        "well_count": len(request.wells),
        "timestamp": _utc_timestamp()
    }

    return {
        "project_name": "Hodgenville Groundwater Supply",
        "client": "City of Hodgenville, KY",
        "well_id": "PW-1",
        "location": "Hodgenville, Kentucky",
        "prepared_by": "Shane Spicer, PE",
        "prepared_for": "Kentucky Division of Water",
        "date": date.today().isoformat(),
        "version": "1.0.0",
        "logo_base64": "",   # Optionally filled in later
        "summary": summary,
        "scenario_wells": payload.get("scenario_wells", [])
    }
