"""Advanced Observability, OpenTelemetry Tracing, Structured JSON Logging, and PII Redaction for Travel Concierge."""

import re
import time
import json
import logging
from typing import Any, Dict, Optional, Union
from google.adk.plugins.base_plugin import BasePlugin

# OpenTelemetry Tracing Integration
try:
    from opentelemetry import trace
    tracer = trace.get_tracer("travel_concierge", "1.0.0")
except ImportError:
    tracer = None


# ---------------------------------------------------------------------------
# 1. PII Redaction Engine
# ---------------------------------------------------------------------------

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
API_KEY_REGEX = re.compile(r"(?i)(key|token|secret|auth|bearer)[\s=:]+[\"']?[A-Za-z0-9_\-]{16,}[\"']?")


def redact_pii(data: Any) -> Any:
    """Recursively redacts PII (emails, phone numbers, credit cards, API keys) from text, dicts, and lists."""
    if isinstance(data, str):
        text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", data)
        text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
        text = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", text)
        text = API_KEY_REGEX.sub(r"\1=[REDACTED_TOKEN]", text)
        return text
    elif isinstance(data, dict):
        return {k: redact_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_pii(item) for item in data]
    return data


# ---------------------------------------------------------------------------
# 2. Structured JSON Logging Formatter
# ---------------------------------------------------------------------------

class StructuredJsonFormatter(logging.Formatter):
    """Logging Formatter that outputs log records as structured JSON strings with PII redaction."""

    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "severity": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        # Merge extra attributes if provided
        if hasattr(record, "structured_data"):
            log_object["data"] = redact_pii(record.structured_data)

        return json.dumps(redact_pii(log_object))


# Setup Structured Logger
logger = logging.getLogger("travel_concierge.observability")
handler = logging.StreamHandler()
handler.setFormatter(StructuredJsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


# ---------------------------------------------------------------------------
# 3. Observability & OpenTelemetry Plugin
# ---------------------------------------------------------------------------

class ObservabilityPlugin(BasePlugin):
    """Advanced Plugin providing OpenTelemetry distributed tracing, structured JSON logging, and PII redaction."""

    def __init__(self, name: str = "observability"):
        super().__init__(name=name)

    async def before_model_callback(self, *, callback_context, llm_request):
        """Logs structured JSON before LLM invocation and starts OpenTelemetry span."""
        agent_name = getattr(callback_context, "agent_name", "unknown_agent")
        model = getattr(llm_request, "model", "unknown_model")

        # Start OpenTelemetry Span
        if tracer:
            span = tracer.start_span("llm_model_request")
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("llm.model", str(model))
            callback_context.state["_otel_llm_span"] = span

        # Structured JSON Log with PII Redaction
        logger.info(
            f"LLM Request Start for agent {agent_name}",
            extra={
                "structured_data": {
                    "event_type": "llm_request_start",
                    "agent": agent_name,
                    "model": str(model),
                }
            }
        )
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        """Logs structured JSON after LLM response completion and ends OpenTelemetry span."""
        agent_name = getattr(callback_context, "agent_name", "unknown_agent")

        # End OpenTelemetry Span
        span = callback_context.state.pop("_otel_llm_span", None)
        if span:
            span.end()

        logger.info(
            f"LLM Response Complete for agent {agent_name}",
            extra={
                "structured_data": {
                    "event_type": "llm_response_complete",
                    "agent": agent_name,
                    "status": "success",
                }
            }
        )
        return None

    async def before_tool_callback(self, *, tool, args, tool_context):
        """Captures before-tool state, redacts PII, logs structured JSON, and starts OpenTelemetry span."""
        tool_name = getattr(tool, "name", str(tool))
        start_time = time.time()
        tool_context.state[f"_tool_start_{tool_name}"] = start_time

        redacted_args = redact_pii(args)

        # OpenTelemetry Span
        if tracer:
            span = tracer.start_span(f"tool_execution:{tool_name}")
            span.set_attribute("tool.name", tool_name)
            tool_context.state[f"_otel_tool_span_{tool_name}"] = span

        logger.info(
            f"Tool Execution Start: {tool_name}",
            extra={
                "structured_data": {
                    "event_type": "tool_execution_start",
                    "tool_name": tool_name,
                    "input_args": redacted_args,
                    "start_time": start_time,
                }
            }
        )
        return None

    async def after_tool_callback(self, *, tool, args, tool_context, tool_response):
        """Captures after-tool state, calculates execution duration, redacts PII, logs structured JSON, and closes span."""
        tool_name = getattr(tool, "name", str(tool))
        start_time = tool_context.state.pop(f"_tool_start_{tool_name}", time.time())
        duration_ms = round((time.time() - start_time) * 1000, 2)

        redacted_response = redact_pii(tool_response)

        # End OpenTelemetry Span
        span = tool_context.state.pop(f"_otel_tool_span_{tool_name}", None)
        if span:
            span.set_attribute("tool.duration_ms", duration_ms)
            span.set_attribute("tool.status", str(tool_response.get("status", "complete")))
            span.end()

        logger.info(
            f"Tool Execution End: {tool_name}",
            extra={
                "structured_data": {
                    "event_type": "tool_execution_end",
                    "tool_name": tool_name,
                    "duration_ms": duration_ms,
                    "status": tool_response.get("status", "complete"),
                    "output": redacted_response,
                }
            }
        )
        return None
