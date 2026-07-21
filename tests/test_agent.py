"""Unit tests for agent instantiation and configuration."""

from travel_concierge.agent import root_agent, app


def test_agent_configuration():
    assert root_agent.name == "travel_concierge"
    assert root_agent.model == "gemini-flash-latest"
    assert len(root_agent.tools) == 3


def test_app_configuration():
    assert app.name == "travel_concierge"
    assert app.root_agent.name == "travel_concierge"
    assert len(app.plugins) == 1
