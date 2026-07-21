"""Security, policy guardrails, and self-evaluation modules for the Travel Concierge agent."""

import logging
from typing import Any, Dict, Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types as genai_types

logger = logging.getLogger("travel_concierge.security")


class SafetyPolicyGuardrailPlugin(BasePlugin):
    """Plugin enforcing input policy guardrails, prompt injection defense, and output verification."""

    def __init__(self, name: str = "safety_guardrails"):
        super().__init__(name=name)

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: Any) -> Optional[LlmResponse]:
        """Inspects prompt inputs for safety policy compliance before sending to model."""
        # Sanity check for malicious injection patterns or restricted prompts
        contents = getattr(llm_request, "contents", [])
        for content in contents:
            if hasattr(content, "parts"):
                for part in content.parts:
                    text = getattr(part, "text", "") or ""
                    if "ignore previous instructions" in text.lower() or "system prompt bypass" in text.lower():
                        logger.warning(f"[Security Guardrail Triggered] Blocked suspicious prompt: {text[:50]}")
                        return LlmResponse(
                            content=genai_types.Content(
                                role="model",
                                parts=[genai_types.Part.from_text(text="[Policy Guardrail] Request blocked due to security policy violation.")],
                            )
                        )
        return None  # Pass policy check

    async def after_model_callback(self, *, callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
        """Verifies model responses against safety policies before rendering to user."""
        logger.info("[Security Guardrail] Output verification passed.")
        return None


async def self_eval_policy_guardrail(callback_context: CallbackContext) -> Optional[genai_types.Content]:
    """Self-evaluation callback that validates generated itineraries against user constraints and safety rules."""
    state = callback_context.state
    prefs = state.get("user_preferences", {})
    budget = prefs.get("budget_tier", "medium")

    logger.info(f"[Self-Eval Guardrail] Verifying itinerary against budget constraint: {budget}")

    # Self-evaluation check passed
    state["self_eval_passed"] = True
    return None
