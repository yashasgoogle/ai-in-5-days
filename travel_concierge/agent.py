"""Travel Concierge Agent definition using Google ADK with Context Management, Database Persistence, and Async Memory Consolidation."""

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.genai import types as genai_types

from travel_concierge.tools import (
    get_weather_forecast,
    get_top_attractions,
    export_itinerary_markdown,
)
from travel_concierge.memory import (
    init_session_state,
    consolidate_memory_background,
    get_session_service,
)
from travel_concierge.observability import ObservabilityPlugin

# Agent System Instruction with Persona & Constraints
SYSTEM_INSTRUCTION = """
You are the Smart Travel Concierge, an expert personal travel planning assistant.

Your Role:
1. Understand the user's destination, length of stay, budget, and travel preferences.
2. Use `get_weather_forecast` to inspect weather conditions during the stay.
3. Use `get_top_attractions` to discover recommended spots by category (culture, food, nature, etc.).
4. Formulate a structured, day-by-day itinerary tailored to user pacing and weather.
5. When the user approves or requests export, call `export_itinerary_markdown` to save the itinerary.

Rules & Constraints:
- Active outdoor activities should be scheduled on clear/sunny weather days.
- Respect user budget level (budget, medium, luxury) and dietary preferences stored in state.
- Maintain context and history across multi-turn user edits.
"""

# Define the root Agent with Async Memory Consolidation Callback
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
    after_agent_callback=consolidate_memory_background,  # Asynchronous background memory consolidation
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2048,
    ),
)

# Persistent Database Session Service
session_service = get_session_service()

# Define App with Context Bloat Management, Context Caching, and Observability
app = App(
    name="travel_concierge",
    root_agent=root_agent,
    plugins=[ObservabilityPlugin(name="observability")],
    # 1. Context Bloat Management: Compacts history every 10 events to prevent token bloat
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
        summarizer=LlmEventSummarizer(llm=root_agent.model),
    ),
    # 2. Context Window Caching: Caches system prompt & instructions when exceeding 2048 tokens
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=5,
    ),
)
