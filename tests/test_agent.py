"""Unit tests for multi-agent architecture, model routing, security guardrails, and HITL hooks."""

import pytest
from travel_concierge.agent import root_agent, app, session_service, export_itinerary_tool
from travel_concierge.security import SafetyPolicyGuardrailPlugin, self_eval_policy_guardrail


def test_multi_agent_architecture_and_model_routing():
    assert root_agent.name == "travel_concierge"
    assert root_agent.model == "gemini-flash-latest"
    assert len(root_agent.sub_agents) == 2

    # Verify Sub-Agent 1 (Destination Researcher - gemini-flash-latest)
    researcher = root_agent.sub_agents[0]
    assert researcher.name == "destination_researcher"
    assert researcher.model == "gemini-flash-latest"

    # Verify Sub-Agent 2 (Itinerary Evaluator - strategic model routing to gemini-pro)
    evaluator = root_agent.sub_agents[1]
    assert evaluator.name == "itinerary_evaluator"
    assert evaluator.model == "gemini-pro"


def test_security_guardrails_and_self_eval():
    # Verify self-eval callback registration
    assert root_agent.after_agent_callback == self_eval_policy_guardrail

    # Verify SafetyPolicyGuardrailPlugin registered on App
    plugin_names = [p.name for p in app.plugins]
    assert "safety_guardrails" in plugin_names


def test_hitl_human_in_the_loop_confirmation():
    # Verify high-stakes export action requires HITL confirmation
    assert export_itinerary_tool.require_confirmation is True

    # Verify App resumability enabled for HITL pause & resume
    assert app.resumability_config is not None
    assert app.resumability_config.is_resumable is True
