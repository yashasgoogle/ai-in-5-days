"""Unit tests for travel concierge function tools."""

import pytest
from travel_concierge.tools import get_weather_forecast, get_top_attractions


def test_get_weather_forecast():
    result = get_weather_forecast("Kyoto", 3)
    assert result["status"] == "success"
    assert result["city"] == "Kyoto"
    assert len(result["forecast"]) == 3
    assert result["forecast"][0]["condition"] == "Sunny"


def test_get_top_attractions():
    result = get_top_attractions("Kyoto", "culture")
    assert result["status"] == "success"
    assert result["city"] == "Kyoto"
    assert result["category"] == "culture"
    assert len(result["attractions"]) >= 1
    assert result["attractions"][0]["name"] == "Fushimi Inari Shrine"
