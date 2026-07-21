"""Tool definitions for the Smart Travel Concierge agent."""

from typing import Any, Dict, List
from google.adk.tools import ToolContext


def get_weather_forecast(city: str, days: int) -> Dict[str, Any]:
    """Retrieves the weather forecast for a given destination city.

    Args:
        city: The destination city name (e.g. 'Kyoto', 'Paris').
        days: Number of forecast days to retrieve (1-7).

    Returns:
        Dict containing weather conditions and average temperature per day.
    """
    # Simulated weather lookup (can be integrated with OpenWeatherMap API)
    mock_weather = {
        "Kyoto": {"condition": "Sunny", "temp_c": 22, "rain_chance": "10%"},
        "Paris": {"condition": "Partly Cloudy", "temp_c": 18, "rain_chance": "20%"},
        "Tokyo": {"condition": "Clear", "temp_c": 24, "rain_chance": "5%"},
    }

    city_data = mock_weather.get(city, {"condition": "Clear", "temp_c": 20, "rain_chance": "15%"})
    forecast = []
    for day in range(1, days + 1):
        forecast.append({
            "day": day,
            "condition": city_data["condition"],
            "temp_c": city_data["temp_c"],
            "rain_chance": city_data["rain_chance"],
        })

    return {"status": "success", "city": city, "forecast": forecast}


def get_top_attractions(city: str, category: str) -> Dict[str, Any]:
    """Retrieves top local attractions for a city filtered by interest category.

    Args:
        city: The destination city name.
        category: Interest category (e.g., 'culture', 'food', 'nature', 'budget').

    Returns:
        Dict containing list of recommended attractions with estimated duration and cost.
    """
    mock_attractions = {
        "Kyoto": {
            "culture": [
                {"name": "Fushimi Inari Shrine", "cost": "Free", "duration": "2-3 hours"},
                {"name": "Kinkaku-ji (Golden Pavilion)", "cost": "$4", "duration": "1-2 hours"},
            ],
            "food": [
                {"name": "Nishiki Market Food Walk", "cost": "$15-25", "duration": "2 hours"},
                {"name": "Gion Traditional Tea House", "cost": "$20", "duration": "1 hour"},
            ],
        }
    }

    city_spots = mock_attractions.get(city, {}).get(
        category,
        [
            {"name": f"Explore central {city}", "cost": "Free", "duration": "2 hours"},
            {"name": f"Local {city} museum", "cost": "$10", "duration": "2 hours"},
        ]
    )

    return {"status": "success", "city": city, "category": category, "attractions": city_spots}


async def export_itinerary_markdown(
    itinerary_title: str,
    content: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Saves the final generated itinerary as a Markdown artifact in the session.

    Args:
        itinerary_title: Name of the itinerary file (e.g. 'kyoto_3day_trip.md').
        content: Complete markdown formatted itinerary text.

    Returns:
        Dict confirming saved status and artifact version.
    """
    from google.genai import types

    blob = types.Part(inline_data=types.Blob(mime_type="text/markdown", data=content.encode("utf-8")))
    version = await tool_context.save_artifact(itinerary_title, blob)

    # Store export flag in session state
    tool_context.state["last_exported_itinerary"] = itinerary_title

    return {
        "status": "success",
        "artifact_name": itinerary_title,
        "version": version,
    }
