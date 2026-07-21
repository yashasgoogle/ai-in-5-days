"""Context and session memory management for the Travel Concierge agent."""

from typing import Any, Dict
from google.adk.agents.callback_context import CallbackContext


async def init_session_state(callback_context: CallbackContext) -> None:
    """Initializes user session state and travel preference keys if not present."""
    state = callback_context.state

    # Initialize travel preference tracking
    if "user_preferences" not in state:
        state["user_preferences"] = {
            "budget_tier": "medium",  # budget, medium, luxury
            "pace": "moderate",       # relaxed, moderate, fast-paced
            "dietary_restrictions": [],
            "favorite_categories": [],
        }

    if "trip_history" not in state:
        state["trip_history"] = []


def update_user_preferences(
    callback_context: CallbackContext,
    budget_tier: str | None = None,
    pace: str | None = None,
    dietary: list[str] | None = None,
) -> None:
    """Updates persistent user travel preferences in session state."""
    prefs = callback_context.state.get("user_preferences", {})

    if budget_tier:
        prefs["budget_tier"] = budget_tier
    if pace:
        prefs["pace"] = pace
    if dietary:
        prefs["dietary_restrictions"] = list(set(prefs.get("dietary_restrictions", []) + dietary))

    callback_context.state["user_preferences"] = prefs
