"""Travel Concierge Agent definition using Google ADK."""

from google.adk.agents import Agent
from google.adk.apps import App
from google.genai import types as genai_types

from travel_concierge.tools import (
    get_weather_forecast,
    get_top_attractions,
    export_itinerary_markdown,
)
from travel_concierge.memory import init_session_state
from travel_concierge.observability import ObservabilityPlugin

# Agent System Instruction
SYSTEM_INSTRUCTION = """
You are the Smart Travel Concierge, an expert personal travel planning assistant.

Your Role:
1. Understand the user's destination, length of stay, budget, and travel preferences.
2. Use `get_weather_forecast` to inspect weather conditions during the stay.
3. Use `get_top_attractions` to discover recommended spots by category (culture, food, nature, etc.).
4. Formulate a structured, day-by-day itinerary tailored to user pacing and weather.
5. When the user approves or requests export, call `export_itinerary_markdown` to save the itinerary.

Rules & Pacing:
- Active outdoor activities should be scheduled on clear/sunny weather days.
- Respect user budget level (budget, medium, luxury).
- Always maintain context across multi-turn user edits.
"""

# Define the root Agent
root_agent = Agent(
    name="travel_concierge",
    model="gemini-flash-latest",
    instruction=SYSTEM_INSTRUCTION,
    description="Smart Travel Concierge agent for custom trip planning.",
    tools=[
        get_weather_forecast,
        get_top_attractions,
        export_itinerary_markdown,
    ],
    before_agent_callback=init_session_state,
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2048,
    ),
)

# Define App with Observability plugin
app = App(
    name="travel_concierge",
    root_agent=root_agent,
    plugins=[ObservabilityPlugin(name="observability")],
)
