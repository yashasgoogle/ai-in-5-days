"""Unit tests for agent instantiation, memory management, and context configuration."""

import pytest
from travel_concierge.agent import root_agent, app, session_service
from travel_concierge.memory import get_session_service, init_session_state, consolidate_memory_background


def test_agent_configuration():
    assert root_agent.name == "travel_concierge"
    assert root_agent.model == "gemini-flash-latest"
    assert len(root_agent.tools) == 3
    assert root_agent.before_agent_callback == init_session_state
    assert root_agent.after_agent_callback == consolidate_memory_background


def test_app_context_bloat_management():
    assert app.name == "travel_concierge"
    assert app.root_agent.name == "travel_concierge"
    assert app.events_compaction_config is not None
    assert app.events_compaction_config.compaction_interval == 10
    assert app.context_cache_config is not None
    assert app.context_cache_config.min_tokens == 2048


def test_session_service_database_persistence():
    service = get_session_service("sqlite:///:memory:")
    assert service is not None
