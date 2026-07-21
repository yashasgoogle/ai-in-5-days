"""Travel Concierge Multi-Agent Architecture using Google ADK.

Features:
1. Multi-Agent System & Strategic Model Routing (Destination Researcher with gemini-flash, Itinerary Evaluator with gemini-pro, and Coordinator).
2. Programmed Human-in-the-Loop (HITL) Hooks (FunctionTool require_confirmation=True for high-stakes itinerary export).
3. Security & Policy Guardrails (SafetyPolicyGuardrailPlugin & self-eval verification callback).
4. Context Bloat Management & Persistent DB Session Storage.
"""

from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.tools import FunctionTool
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
from travel_concierge.security import SafetyPolicyGuardrailPlugin, self_eval_policy_guardrail


# ---------------------------------------------------------------------------
# 1. High-Stakes Action with Programmed Human-In-The-Loop (HITL) Confirmation
# ---------------------------------------------------------------------------

# Wrap high-stakes export action with FunctionTool confirmation requirement
export_itinerary_tool = FunctionTool(
    export_itinerary_markdown,
    require_confirmation=True,  # Triggers HITL confirmation before writing artifacts/files
)


# ---------------------------------------------------------------------------
# 2. Multi-Agent Sub-Agents & Strategic Model Routing
# ---------------------------------------------------------------------------

def create_destination_researcher() -> Agent:
    """Specialized Sub-Agent 1: Fast research agent routed to gemini-flash-latest."""
    return Agent(
        name="destination_researcher",
        model="gemini-flash-latest",
        instruction="""
        You are a Destination Research Specialist.
        Your job is to use `get_weather_forecast` and `get_top_attractions` to gather comprehensive data on weather conditions and spots for the destination.
        """,
        description="Researches weather forecasts and top attractions for the trip destination.",
        tools=[get_weather_forecast, get_top_attractions],
        output_key="research_data",
    )


def create_itinerary_evaluator() -> Agent:
    """Specialized Sub-Agent 2: High-reasoning self-evaluator agent routed to gemini-pro."""
    return Agent(
        name="itinerary_evaluator",
        model="gemini-pro",  # Strategic model routing: Higher reasoning model for constraint evaluation
        instruction="""
        You are an Itinerary Quality & Safety Evaluator.
        Your job is to evaluate proposed trip itineraries against safety rules, budget constraints, and dietary preferences stored in state.
        """,
        description="Evaluates proposed travel plans against safety guidelines, user budget, and dietary constraints.",
        output_key="evaluation_report",
    )


# ---------------------------------------------------------------------------
# 3. Root Coordinator Agent with Self-Eval Guardrail & Async Memory Callback
# ---------------------------------------------------------------------------

COORDINATOR_INSTRUCTION = """
You are the Smart Travel Concierge Coordinator.

Your Role:
1. Coordinate trip planning by delegating destination research to `destination_researcher` and quality checks to `itinerary_evaluator`.
2. Formulate a structured, day-by-day itinerary tailored to user pacing and weather.
3. When the user approves export, invoke `export_itinerary_markdown` (which requires Human-In-The-Loop confirmation).

Rules & Policy Constraints:
- Outdoor activities must be scheduled on clear weather days.
- Respect user budget tier and dietary restrictions.
"""

root_agent = Agent(
    name="travel_concierge",
    model="gemini-flash-latest",
    instruction=COORDINATOR_INSTRUCTION,
    description="Smart Travel Concierge multi-agent coordinator for custom trip planning.",
    sub_agents=[
        create_destination_researcher(),
        create_itinerary_evaluator(),
    ],
    tools=[
        get_weather_forecast,
        get_top_attractions,
        export_itinerary_tool,  # High-stakes HITL confirmation tool
    ],
    before_agent_callback=init_session_state,
    after_agent_callback=self_eval_policy_guardrail,  # Explicit Self-Eval Policy Guardrail
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2048,
    ),
)


# Persistent Database Session Storage Service
session_service = get_session_service()

# ---------------------------------------------------------------------------
# 4. App Definition with Plugins, HITL Resumability, & Context Management
# ---------------------------------------------------------------------------

app = App(
    name="travel_concierge",
    root_agent=root_agent,
    plugins=[
        ObservabilityPlugin(name="observability"),
        SafetyPolicyGuardrailPlugin(name="safety_guardrails"),  # Policy Guardrail Plugin
    ],
    # Resumability config for Human-in-the-Loop pause & resume
    resumability_config=ResumabilityConfig(is_resumable=True),
    # Context Bloat Management
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
        summarizer=LlmEventSummarizer(llm=root_agent.model),
    ),
    # Context Window Caching
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=5,
    ),
)
