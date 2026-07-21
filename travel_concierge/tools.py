"""Tool definitions for the Smart Travel Concierge agent with Pydantic schema validation and guided LLM error recovery."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError
from google.adk.tools import ToolContext


# ---------------------------------------------------------------------------
# Pydantic Schemas for Strict Input & Output Validation
# ---------------------------------------------------------------------------

class WeatherForecastInput(BaseModel):
    city: str = Field(..., min_length=1, description="Destination city name (e.g., 'Kyoto', 'Paris').")
    days: int = Field(..., ge=1, le=7, description="Number of forecast days to retrieve (must be between 1 and 7).")


class DailyWeather(BaseModel):
    day: int
    condition: str
    temp_c: int
    rain_chance: str


class WeatherForecastResponse(BaseModel):
    status: str = Field(..., description="Execution status: 'success' or 'error'.")
    city: Optional[str] = None
    forecast: Optional[List[DailyWeather]] = None
    error_message: Optional[str] = None
    recovery_instruction: Optional[str] = None


class AttractionsInput(BaseModel):
    city: str = Field(..., min_length=1, description="Destination city name.")
    category: str = Field(..., description="Interest category: 'culture', 'food', 'nature', or 'budget'.")


class AttractionSpot(BaseModel):
    name: str
    cost: str
    duration: str


class AttractionsResponse(BaseModel):
    status: str = Field(..., description="Execution status: 'success' or 'error'.")
    city: Optional[str] = None
    category: Optional[str] = None
    attractions: Optional[List[AttractionSpot]] = None
    error_message: Optional[str] = None
    recovery_instruction: Optional[str] = None


class ExportItineraryInput(BaseModel):
    itinerary_title: str = Field(..., min_length=3, description="Name of the itinerary file (must end in .md, e.g. 'kyoto_3day_trip.md').")
    content: str = Field(..., min_length=10, description="Complete Markdown formatted itinerary content.")


class ExportItineraryResponse(BaseModel):
    status: str = Field(..., description="Execution status: 'success' or 'error'.")
    artifact_name: Optional[str] = None
    version: Optional[int] = None
    error_message: Optional[str] = None
    recovery_instruction: Optional[str] = None


# ---------------------------------------------------------------------------
# Tools with Guided Error Handling and Recovery Instructions
# ---------------------------------------------------------------------------

def get_weather_forecast(city: str, days: int) -> Dict[str, Any]:
    """Retrieves the weather forecast for a given destination city.

    Args:
        city: The destination city name (e.g. 'Kyoto', 'Paris').
        days: Number of forecast days to retrieve (1-7).

    Returns:
        Dict containing validated WeatherForecastResponse data with status and guided recovery on error.
    """
    # 1. Input Validation using Pydantic
    try:
        validated_input = WeatherForecastInput(city=city, days=days)
    except ValidationError as ve:
        error_res = WeatherForecastResponse(
            status="error",
            error_message=f"Invalid arguments provided: {ve.errors()[0]['msg']}",
            recovery_instruction="The 'days' parameter must be an integer between 1 and 7, and 'city' must be a non-empty string. Please adjust parameters and try again."
        )
        return error_res.model_dump()

    # 2. Tool Execution & Error Handling
    try:
        clean_city = validated_input.city.strip().title()
        mock_weather = {
            "Kyoto": {"condition": "Sunny", "temp_c": 22, "rain_chance": "10%"},
            "Paris": {"condition": "Partly Cloudy", "temp_c": 18, "rain_chance": "20%"},
            "Tokyo": {"condition": "Clear", "temp_c": 24, "rain_chance": "5%"},
        }

        city_data = mock_weather.get(clean_city, {"condition": "Clear", "temp_c": 20, "rain_chance": "15%"})
        forecast = [
            DailyWeather(
                day=d,
                condition=city_data["condition"],
                temp_c=city_data["temp_c"],
                rain_chance=city_data["rain_chance"],
            )
            for d in range(1, validated_input.days + 1)
        ]

        response = WeatherForecastResponse(
            status="success",
            city=clean_city,
            forecast=forecast,
        )
        return response.model_dump()

    except Exception as e:
        error_res = WeatherForecastResponse(
            status="error",
            error_message=f"Weather lookup failed: {str(e)}",
            recovery_instruction="Failed to process weather request. Verify city name spelling and retry."
        )
        return error_res.model_dump()


def get_top_attractions(city: str, category: str) -> Dict[str, Any]:
    """Retrieves top local attractions for a city filtered by interest category.

    Args:
        city: The destination city name.
        category: Interest category (supported: 'culture', 'food', 'nature', 'budget').

    Returns:
        Dict containing validated AttractionsResponse data with guided recovery instructions on error.
    """
    valid_categories = ["culture", "food", "nature", "budget"]

    # 1. Input Validation using Pydantic
    try:
        validated_input = AttractionsInput(city=city, category=category)
    except ValidationError as ve:
        error_res = AttractionsResponse(
            status="error",
            error_message=f"Invalid input: {ve.errors()[0]['msg']}",
            recovery_instruction=f"Category must be one of: {', '.join(valid_categories)}. Please retry with a valid category."
        )
        return error_res.model_dump()

    # 2. Category Check
    clean_category = validated_input.category.strip().lower()
    if clean_category not in valid_categories:
        error_res = AttractionsResponse(
            status="error",
            category=clean_category,
            error_message=f"Unsupported category '{clean_category}'.",
            recovery_instruction=f"Supported categories are: {', '.join(valid_categories)}. Please call get_top_attractions using one of these categories."
        )
        return error_res.model_dump()

    # 3. Tool Execution
    try:
        clean_city = validated_input.city.strip().title()
        mock_attractions = {
            "Kyoto": {
                "culture": [
                    AttractionSpot(name="Fushimi Inari Shrine", cost="Free", duration="2-3 hours"),
                    AttractionSpot(name="Kinkaku-ji (Golden Pavilion)", cost="$4", duration="1-2 hours"),
                ],
                "food": [
                    AttractionSpot(name="Nishiki Market Food Walk", cost="$15-25", duration="2 hours"),
                    AttractionSpot(name="Gion Traditional Tea House", cost="$20", duration="1 hour"),
                ],
            }
        }

        city_spots = mock_attractions.get(clean_city, {}).get(
            clean_category,
            [
                AttractionSpot(name=f"Explore central {clean_city}", cost="Free", duration="2 hours"),
                AttractionSpot(name=f"Local {clean_city} museum", cost="$10", duration="2 hours"),
            ]
        )

        response = AttractionsResponse(
            status="success",
            city=clean_city,
            category=clean_category,
            attractions=city_spots,
        )
        return response.model_dump()

    except Exception as e:
        error_res = AttractionsResponse(
            status="error",
            error_message=f"Attractions lookup failed: {str(e)}",
            recovery_instruction="An internal error occurred. Try searching again with a major city name."
        )
        return error_res.model_dump()


async def export_itinerary_markdown(
    itinerary_title: str,
    content: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Saves the final generated itinerary as a Markdown artifact in the session.

    Args:
        itinerary_title: Name of the itinerary file (must end in .md, e.g. 'kyoto_3day_trip.md').
        content: Complete markdown formatted itinerary text.

    Returns:
        Dict containing validated ExportItineraryResponse data with guided recovery instructions on error.
    """
    # 1. Input Validation using Pydantic
    try:
        validated_input = ExportItineraryInput(itinerary_title=itinerary_title, content=content)
    except ValidationError as ve:
        error_res = ExportItineraryResponse(
            status="error",
            error_message=f"Validation error: {ve.errors()[0]['msg']}",
            recovery_instruction="Ensure itinerary_title is at least 3 characters and content has at least 10 characters."
        )
        return error_res.model_dump()

    # 2. Format Validation
    if not validated_input.itinerary_title.endswith(".md"):
        error_res = ExportItineraryResponse(
            status="error",
            error_message="Filename extension must be '.md'.",
            recovery_instruction="Please provide an itinerary_title ending with '.md' (e.g., 'trip_itinerary.md')."
        )
        return error_res.model_dump()

    # 3. Tool Execution & Artifact Saving
    try:
        from google.genai import types

        blob = types.Part(inline_data=types.Blob(mime_type="text/markdown", data=validated_input.content.encode("utf-8")))
        version = await tool_context.save_artifact(validated_input.itinerary_title, blob)

        # Store export flag in session state
        tool_context.state["last_exported_itinerary"] = validated_input.itinerary_title

        response = ExportItineraryResponse(
            status="success",
            artifact_name=validated_input.itinerary_title,
            version=version,
        )
        return response.model_dump()

    except Exception as e:
        error_res = ExportItineraryResponse(
            status="error",
            error_message=f"Failed to save artifact: {str(e)}",
            recovery_instruction="Verify tool context and content format, then retry export."
        )
        return error_res.model_dump()
