"""Integration tests for the gateway server."""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport, Response

from gateway.server import app
from gateway.openwa_client import send_message


class TestWebhookEndpoint:
    """End-to-end: webhook → parse → echo → send."""

    @pytest.mark.asyncio
    async def test_english_message_flow(self):
        """POST English message → greeting + escalation sent via OpenWA."""
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/webhook",
                    json={
                        "event": "message",
                        "data": {
                            "from": "1234567890@c.us",
                            "to": "0987654321@c.us",
                            "body": "Hi, any appointments today?",
                            "type": "chat",
                            "notifyName": "John Smith",
                        },
                    },
                )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Unified gateway: new patient greeting + escalation (no FAQ match)
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["to"] == "1234567890@c.us"
        assert "Welcome to Laredo Dental" in call_args.kwargs["body"]
        assert "sent your question" in call_args.kwargs["body"]
        assert call_args.kwargs["openwa_url"] == "http://localhost:3000"

    @pytest.mark.asyncio
    async def test_spanish_message_flow(self):
        """POST Spanish message → Spanish greeting + escalation sent via OpenWA."""
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/webhook",
                    json={
                        "event": "message",
                        "data": {
                            "from": "521234567890@c.us",
                            "to": "521987654321@c.us",
                            "body": "Hola, ¿tienen cita para mañana?",
                            "type": "chat",
                            "notifyName": "María García",
                        },
                    },
                )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Unified gateway: Spanish new patient greeting + escalation (no FAQ match)
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["to"] == "521234567890@c.us"
        assert "Bienvenido a Laredo Dental" in call_args.kwargs["body"]
        assert "sent your question" in call_args.kwargs["body"]
        assert call_args.kwargs["openwa_url"] == "http://localhost:3000"

    @pytest.mark.asyncio
    async def test_rejects_non_message_events(self):
        """Return 400 for non-message events."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/webhook",
                json={
                    "event": "status",
                    "data": {},
                },
            )

        assert response.status_code == 400
        assert "Unsupported event" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_returns_502_when_openwa_fails(self):
        """Return 502 when OpenWA send fails."""
        mock_send = AsyncMock(return_value=False)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/webhook",
                    json={
                        "event": "message",
                        "data": {
                            "from": "1234567890@c.us",
                            "to": "0987654321@c.us",
                            "body": "Test",
                            "type": "chat",
                            "notifyName": "Test",
                        },
                    },
                )

        assert response.status_code == 502
        assert "Failed to send" in response.json()["detail"]


class TestHealthEndpoint:
    """Health check for monitoring."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        """GET /health returns 200 with healthy status."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        # Unified gateway includes extra fields — just verify they exist
        assert "patients" in data
        assert "faq_topics" in data
