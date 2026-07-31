"""Tests for echo response handler."""
from gateway.handler import build_echo_response


class TestBuildEchoResponse:
    """Build echo response from parsed message."""

    def test_echoes_english_message(self):
        """Return 'Received: {body}' for English message."""
        parsed = {
            "from": "1234567890@c.us",
            "body": "Hi, do you have appointments?",
            "notify_name": "John Smith",
        }

        response = build_echo_response(parsed)

        assert response["to"] == "1234567890@c.us"
        assert response["body"] == "Received: Hi, do you have appointments?"

    def test_echoes_spanish_message(self):
        """Return 'Received: {body}' for Spanish message."""
        parsed = {
            "from": "521234567890@c.us",
            "body": "Hola, ¿tienen cita disponible?",
            "notify_name": "María García",
        }

        response = build_echo_response(parsed)

        assert response["to"] == "521234567890@c.us"
        assert response["body"] == "Received: Hola, ¿tienen cita disponible?"

    def test_echoes_spanglish_message(self):
        """Handle mixed English/Spanish gracefully."""
        parsed = {
            "from": "1234567890@c.us",
            "body": "Hi, necesito una cita for tomorrow",
            "notify_name": "Ana López",
        }

        response = build_echo_response(parsed)

        assert response["to"] == "1234567890@c.us"
        assert response["body"] == "Received: Hi, necesito una cita for tomorrow"
