"""Unit tests for travel concierge function tools with Pydantic validation and error recovery."""

import pytest
from travel_concierge.tools import (
    get_weather_forecast,
    get_top_attractions,
    export_itinerary_markdown,
)


def test_get_weather_forecast_success():
    result = get_weather_forecast("Kyoto", 3)
    assert result["status"] == "success"
    assert result["city"] == "Kyoto"
    assert len(result["forecast"]) == 3
    assert result["forecast"][0]["condition"] == "Sunny"


def test_get_weather_forecast_invalid_days():
    # Days parameter out of range (8 > 7)
    result = get_weather_forecast("Kyoto", 8)
    assert result["status"] == "error"
    assert "error_message" in result
    assert "recovery_instruction" in result
    assert "1 and 7" in result["recovery_instruction"]


def test_get_top_attractions_success():
    result = get_top_attractions("Kyoto", "culture")
    assert result["status"] == "success"
    assert result["city"] == "Kyoto"
    assert result["category"] == "culture"
    assert len(result["attractions"]) >= 1
    assert result["attractions"][0]["name"] == "Fushimi Inari Shrine"


def test_get_top_attractions_unsupported_category():
    result = get_top_attractions("Kyoto", "unsupported_category")
    assert result["status"] == "error"
    assert "error_message" in result
    assert "recovery_instruction" in result
    assert "Supported categories" in result["recovery_instruction"]
