"""Integration tests for the gateway server."""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport, Response

from gateway.server import app
from gateway.openwa_client import send_message


class TestWebhookEndpoint:
    """End-to-end: webhook → verify → record → respond → send."""

    @pytest.mark.asyncio
    async def test_records_conversation_on_message(self):
        """Each incoming message is recorded in PatientStore."""
        from gateway.server import create_app
        from memory.store import PatientStore

        store = PatientStore()
        app = create_app(store=store)
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.post("/webhook", json={
                    "event": "message",
                    "data": {
                        "from": "1234567890@c.us",
                        "to": "x@c.us",
                        "body": "Hi, what time do you open?",
                        "type": "chat",
                        "notifyName": "John Smith",
                    },
                })

        assert store.get_conversation_count("1234567890@c.us") == 1
        history = store.get_conversation_history("1234567890@c.us")
        assert history[0]["message"] == "Hi, what time do you open?"
        assert "timestamp" in history[0]

    @pytest.mark.asyncio
    async def test_known_name_different_phone_triggers_verification(self):
        """When a known patient name messages from a new phone, verification triggers."""
        from gateway.server import create_app
        from memory.store import PatientStore
        from datetime import date

        store = PatientStore()
        store.add("phone1@c.us", "María García", date(2026, 7, 15))
        app = create_app(store=store)
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.post("/webhook", json={
                    "event": "message",
                    "data": {
                        "from": "phone2@c.us",
                        "to": "x@c.us",
                        "body": "Hola, soy María García",
                        "type": "chat",
                        "notifyName": "María García",
                    },
                })

        mock_send.assert_called_once()
        body = mock_send.call_args.kwargs["body"]
        assert "María" in body
        assert "different number" in body.lower() or "número diferente" in body.lower()

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


class TestIntakeFlow:
    """New patient intake: multi-turn conversation through webhook."""

    @pytest.mark.asyncio
    async def test_new_patient_triggers_intake(self):
        """Asking about new patient starts the intake flow."""
        from gateway.server import create_app
        from memory.store import PatientStore

        store = PatientStore()
        app = create_app(store=store)
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/webhook", json={
                    "event": "message",
                    "data": {
                        "from": "521234567890@c.us",
                        "to": "x@c.us",
                        "body": "Soy nuevo paciente",
                        "type": "chat",
                        "notifyName": "María García",
                    },
                })

        assert response.status_code == 200
        mock_send.assert_called_once()
        body = mock_send.call_args.kwargs["body"]
        assert "nombre" in body.lower() or "name" in body.lower()

    @pytest.mark.asyncio
    async def test_intake_collects_name_and_time(self):
        """Multi-turn intake: name → time_slot → confirm → done."""
        from gateway.server import create_app
        from memory.store import PatientStore

        store = PatientStore()
        app = create_app(store=store)
        mock_send = AsyncMock(return_value=True)

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Turn 1: trigger intake
                await client.post("/webhook", json={
                    "event": "message", "data": {
                        "from": "1234567890@c.us", "to": "x@c.us",
                        "body": "I'm a new patient", "type": "chat",
                        "notifyName": "John Smith",
                    },
                })
                # Turn 2: give name
                await client.post("/webhook", json={
                    "event": "message", "data": {
                        "from": "1234567890@c.us", "to": "x@c.us",
                        "body": "John Smith", "type": "chat",
                        "notifyName": "John Smith",
                    },
                })
                # Turn 3: give time
                await client.post("/webhook", json={
                    "event": "message", "data": {
                        "from": "1234567890@c.us", "to": "x@c.us",
                        "body": "Friday at 2pm", "type": "chat",
                        "notifyName": "John Smith",
                    },
                })
                # Turn 4: confirm
                await client.post("/webhook", json={
                    "event": "message", "data": {
                        "from": "1234567890@c.us", "to": "x@c.us",
                        "body": "yes", "type": "chat",
                        "notifyName": "John Smith",
                    },
                })

        assert mock_send.call_count == 4
        # Last call should be the done confirmation
        final_body = mock_send.call_args_list[-1].kwargs["body"]
        assert "saved" in final_body.lower() or "call you" in final_body.lower()
