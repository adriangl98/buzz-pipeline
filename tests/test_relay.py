"""Tests for SMS relay to dental office owner."""
import pytest
from unittest.mock import AsyncMock, patch
from escalation.relay import SMSRelay


class TestSMSRelay:
    """Relay escalation messages between agent and owner."""

    def test_builds_owner_alert(self):
        """Build an SMS alert for the owner with patient context."""
        relay = SMSRelay(owner_phone="+15551234567")

        message = relay.build_alert(
            patient_name="María García",
            patient_phone="521234567890@c.us",
            question="¿Necesito una endodoncia?",
            reason="medical_advice",
        )

        assert "María García" in message
        assert "521234567890" in message
        assert "medical" in message.lower()
        assert len(message) < 320  # SMS-friendly length

    @pytest.mark.asyncio
    async def test_sends_alert_via_openwa(self):
        """Send alert to owner using OpenWA client."""
        relay = SMSRelay(owner_phone="+15551234567")
        mock_send = AsyncMock(return_value=True)

        with patch("escalation.relay.send_message", mock_send):
            success = await relay.alert_owner(
                patient_name="María García",
                patient_phone="521234567890@c.us",
                question="¿Necesito una endodoncia?",
                reason="medical_advice",
            )

        assert success is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["to"] == "+15551234567"
        assert "María García" in call_args.kwargs["body"]

    @pytest.mark.asyncio
    async def test_relay_owner_reply_to_patient(self):
        """Owner replies → relay to the original patient."""
        relay = SMSRelay(owner_phone="+15551234567")
        mock_send = AsyncMock(return_value=True)

        with patch("escalation.relay.send_message", mock_send):
            success = await relay.relay_to_patient(
                patient_phone="521234567890@c.us",
                owner_reply="Sí, María necesita evaluación. Agendar cita la próxima semana.",
            )

        assert success is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["to"] == "521234567890@c.us"
        assert "María" in call_args.kwargs["body"]

    @pytest.mark.asyncio
    async def test_handles_send_failure_gracefully(self):
        """Return False when OpenWA send fails."""
        relay = SMSRelay(owner_phone="+15551234567")
        mock_send = AsyncMock(return_value=False)

        with patch("escalation.relay.send_message", mock_send):
            success = await relay.alert_owner(
                patient_name="Test",
                patient_phone="521234567890@c.us",
                question="Test question",
                reason="unknown",
            )

        assert success is False
