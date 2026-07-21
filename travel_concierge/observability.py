"""Observability, telemetry, and tracing plugins for the Travel Concierge agent."""

import logging
from google.adk.plugins.base_plugin import BasePlugin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("travel_concierge")


class ObservabilityPlugin(BasePlugin):
    """Plugin for logging agent events, model execution latency, and tool invocations."""

    def __init__(self, name: str = "observability"):
        super().__init__(name=name)

    async def before_model_callback(self, *, callback_context, llm_request):
        """Logs outgoing model requests."""
        logger.info(f"[LLM Request] Agent: {callback_context.agent_name} | Model: {llm_request.model}")
        return None  # Pass through to model

    async def after_model_callback(self, *, callback_context, llm_response):
        """Logs model response completion."""
        logger.info(f"[LLM Response] Agent: {callback_context.agent_name} | Response received.")
        return None  # Pass through response

    async def before_tool_callback(self, *, tool, args, tool_context):
        """Logs tool execution start and arguments."""
        logger.info(f"[Tool Execution Start] Tool: {tool.name} | Args: {args}")
        return None  # Continue execution

    async def after_tool_callback(self, *, tool, args, tool_context, tool_response):
        """Logs tool execution output status."""
        logger.info(f"[Tool Execution End] Tool: {tool.name} | Status: {tool_response.get('status', 'complete')}")
        return None  # Continue execution
