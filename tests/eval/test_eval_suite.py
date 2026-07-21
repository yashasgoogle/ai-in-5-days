"""Automated regression evaluation suite executing tests against the golden dataset."""

import json
import pathlib
import pytest

from travel_concierge.tools import get_weather_forecast, get_top_attractions


def load_golden_dataset():
    dataset_path = pathlib.Path(__file__).parent / "datasets" / "golden_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_golden_dataset_structure():
    data = load_golden_dataset()
    assert "eval_cases" in data
    assert len(data["eval_cases"]) >= 3


@pytest.mark.parametrize("case", load_golden_dataset()["eval_cases"])
def test_golden_case_tool_execution(case):
    """Executes regression evaluation against golden dataset cases."""
    case_id = case["eval_case_id"]

    if case_id == "kyoto_culture_query":
        weather_res = get_weather_forecast("Kyoto", 3)
        attraction_res = get_top_attractions("Kyoto", "culture")

        assert weather_res["status"] == "success"
        assert attraction_res["status"] == "success"
        assert "Fushimi Inari Shrine" in [a["name"] for a in attraction_res["attractions"]]

    elif case_id == "paris_food_query":
        attraction_res = get_top_attractions("Paris", "food")
        assert attraction_res["status"] == "success"

    elif case_id == "invalid_days_recovery":
        weather_res = get_weather_forecast("Kyoto", 10)
        assert weather_res["status"] == "error"
        assert "recovery_instruction" in weather_res
        assert "1 and 7" in weather_res["recovery_instruction"]
