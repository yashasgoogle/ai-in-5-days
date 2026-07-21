"""Context and session memory management for the Travel Concierge agent.

Includes:
1. Persistent database session state integration (DatabaseSessionService / InMemorySessionService).
2. Asynchronous background task for memory consolidation into long-term user memory.
3. User preference state tracking.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import InMemorySessionService, DatabaseSessionService

logger = logging.getLogger("travel_concierge.memory")


# ---------------------------------------------------------------------------
# 1. Persistent Database Integration for Session State
# ---------------------------------------------------------------------------

def get_session_service(db_url: Optional[str] = None):
    """Factory function providing persistent database session storage for session state.

    Args:
        db_url: Connection URL for persistent DB storage (e.g. 'sqlite:///sessions.db').
                If omitted, checks DATABASE_URL env or defaults to SQLite persistence.

    Returns:
        Configured SessionService instance (DatabaseSessionService or InMemorySessionService fallback).
    """
    target_url = db_url or os.environ.get("DATABASE_URL", "sqlite:///sessions.db")

    try:
        logger.info(f"Initializing DatabaseSessionService with URI: {target_url}")
        return DatabaseSessionService(db_url=target_url)
    except Exception as e:
        logger.warning(f"DatabaseSessionService init failed ({str(e)}), falling back to InMemorySessionService.")
        return InMemorySessionService()


# ---------------------------------------------------------------------------
# 2. Session State & Preference Tracking
# ---------------------------------------------------------------------------

async def init_session_state(callback_context: CallbackContext) -> None:
    """Initializes user session state, trip history, and user-persistent memory."""
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

    # Initialize user-persistent long-term memory prefix if not present
    if "user:persistent_memory" not in state:
        state["user:persistent_memory"] = {
            "saved_trips_count": 0,
            "frequent_destinations": [],
            "consolidated_preferences": {},
        }


def update_user_preferences(
    callback_context: CallbackContext,
    budget_tier: Optional[str] = None,
    pace: Optional[str] = None,
    dietary: Optional[List[str]] = None,
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


# ---------------------------------------------------------------------------
# 3. Asynchronous Background Task for Memory Consolidation
# ---------------------------------------------------------------------------

async def consolidate_memory_background(callback_context: CallbackContext) -> None:
    """Asynchronous background task triggered after agent turns to consolidate short-term session events into long-term user memory.

    Executes non-blockingly without delaying the primary user response loop.
    """
    async def _async_memory_worker():
        try:
            state = callback_context.state
            prefs = state.get("user_preferences", {})
            history = state.get("trip_history", [])

            # Consolidate user memory summary
            frequent_cities = list(set([t["city"] for t in history if isinstance(t, dict) and "city" in t]))
            
            consolidated_memory = {
                "saved_trips_count": len(history),
                "frequent_destinations": frequent_cities,
                "consolidated_preferences": {
                    "budget": prefs.get("budget_tier"),
                    "pace": prefs.get("pace"),
                    "dietary": prefs.get("dietary_restrictions", []),
                },
            }

            # Update long-term user-persistent state
            state["user:persistent_memory"] = consolidated_memory
            logger.info(f"[Background Memory Consolidation Complete] Consolidated {len(history)} trips for user.")

        except Exception as err:
            logger.error(f"[Background Memory Consolidation Error]: {str(err)}")

    # Schedule as a non-blocking background task
    asyncio.create_task(_async_memory_worker())
