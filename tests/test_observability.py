"""Unit tests for PII redaction, structured JSON logging, and OpenTelemetry observability."""

import json
import logging
import pytest
from travel_concierge.observability import redact_pii, StructuredJsonFormatter, ObservabilityPlugin


def test_pii_redaction():
    raw_data = {
        "user_email": "alice@example.com",
        "contact_phone": "555-123-4567",
        "card": "4111-1111-1111-1111",
        "secret_token": "bearer secret_key_1234567890",
        "city": "Kyoto",
    }

    redacted = redact_pii(raw_data)

    assert redacted["user_email"] == "[REDACTED_EMAIL]"
    assert redacted["contact_phone"] == "[REDACTED_PHONE]"
    assert redacted["card"] == "[REDACTED_CARD]"
    assert "REDACTED_TOKEN" in redacted["secret_token"]
    assert redacted["city"] == "Kyoto"  # Non-PII untouched


def test_structured_json_formatter():
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message with user email user@domain.com",
        args=(),
        exc_info=None,
    )
    record.structured_data = {"email": "user@domain.com", "action": "test"}

    formatted_output = formatter.format(record)
    json_obj = json.loads(formatted_output)

    assert json_obj["severity"] == "INFO"
    assert "[REDACTED_EMAIL]" in json_obj["event"]
    assert json_obj["data"]["email"] == "[REDACTED_EMAIL]"
