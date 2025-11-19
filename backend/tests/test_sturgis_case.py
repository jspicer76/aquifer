import json
from pathlib import Path

import pytest

from backend.src.main import main


STURGIS_PATH = Path(__file__).resolve().parents[1] / "testcases" / "sturgis_case.json"


@pytest.fixture(scope="module")
def sturgis_payload():
    return json.loads(STURGIS_PATH.read_text())


def test_sturgis_case_calibration_and_drawdown(sturgis_payload):
    results = main(custom_inputs=sturgis_payload, generate_report=False)

    assert results["aquifer_class"]["type"] == "Unconfined Aquifer"
    assert pytest.approx(99.9001, rel=0.05) == results["calibrated"]["T"]
    assert pytest.approx(0.07607, rel=0.05) == results["calibrated"]["Sy"]
    assert pytest.approx(0.00442, rel=0.2) == results["pump72"]["max_drawdown_ft"]


def test_sturgis_case_boundaries_are_parsed(sturgis_payload):
    results = main(custom_inputs=sturgis_payload, generate_report=False)

    boundaries = results.get("boundaries") or {}
    assert boundaries["constant_head"][0]["head"] == 85
    assert len(boundaries["no_flow"]) == 3
