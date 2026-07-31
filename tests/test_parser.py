"""Tests for OpenWA webhook parser."""
import pytest
from gateway.parser import parse_webhook


class TestParseWebhook:
    """Parse incoming OpenWA webhook payloads."""

    def test_parses_english_message(self):
        """Extract from, body, and notifyName from an English message."""
        payload = {
            "event": "message",
            "data": {
                "from": "1234567890@c.us",
                "to": "0987654321@c.us",
                "body": "Hi, do you have appointments available?",
                "type": "chat",
                "notifyName": "John Smith",
            },
        }

        result = parse_webhook(payload)

        assert result["from"] == "1234567890@c.us"
        assert result["body"] == "Hi, do you have appointments available?"
        assert result["notify_name"] == "John Smith"

    def test_parses_spanish_message(self):
        """Extract from, body, and notifyName from a Spanish message."""
        payload = {
            "event": "message",
            "data": {
                "from": "521234567890@c.us",
                "to": "521987654321@c.us",
                "body": "Hola, ¿tienen cita disponible para mañana?",
                "type": "chat",
                "notifyName": "María García",
            },
        }

        result = parse_webhook(payload)

        assert result["from"] == "521234567890@c.us"
        assert result["body"] == "Hola, ¿tienen cita disponible para mañana?"
        assert result["notify_name"] == "María García"

    def test_rejects_non_message_event(self):
        """Raise ValueError for non-message events."""
        payload = {
            "event": "status",
            "data": {},
        }

        with pytest.raises(ValueError, match="Unsupported event: status"):
            parse_webhook(payload)

    def test_rejects_missing_fields(self):
        """Raise ValueError when required fields are missing."""
        payload = {
            "event": "message",
            "data": {
                "from": "1234567890@c.us",
            },
        }

        with pytest.raises(ValueError, match="Missing required field"):
            parse_webhook(payload)
