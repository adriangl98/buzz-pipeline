"""Tests for OpenWA client."""
import pytest
from unittest.mock import AsyncMock, patch
import httpx
from gateway.openwa_client import send_message


class TestSendMessage:
    """Send messages back to WhatsApp via OpenWA API."""

    @pytest.mark.asyncio
    async def test_sends_text_to_openwa(self):
        """POSTs correct payload to OpenWA /api/sendText."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = httpx.Response(200, json={"success": True})
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client

        with patch("gateway.openwa_client.httpx.AsyncClient", return_value=mock_client):
            result = await send_message(
                to="1234567890@c.us",
                body="Received: Hello",
                openwa_url="http://localhost:3000",
            )

        assert result is True
        mock_client.post.assert_called_once_with(
            "http://localhost:3000/api/sendText",
            json={"chatId": "1234567890@c.us", "text": "Received: Hello"},
            timeout=5.0,
        )

    @pytest.mark.asyncio
    async def test_sends_spanish_text_to_openwa(self):
        """POSTs Spanish text correctly."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = httpx.Response(200, json={"success": True})
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client

        with patch("gateway.openwa_client.httpx.AsyncClient", return_value=mock_client):
            result = await send_message(
                to="521234567890@c.us",
                body="Received: Hola, ¿tienen cita?",
                openwa_url="http://localhost:3000",
            )

        assert result is True
        mock_client.post.assert_called_once_with(
            "http://localhost:3000/api/sendText",
            json={
                "chatId": "521234567890@c.us",
                "text": "Received: Hola, ¿tienen cita?",
            },
            timeout=5.0,
        )

    @pytest.mark.asyncio
    async def test_returns_false_on_http_error(self):
        """Return False when OpenWA returns non-200 status."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = httpx.Response(500, json={"error": "internal"})
        mock_client.post.return_value = mock_response

        with patch("gateway.openwa_client.httpx.AsyncClient", return_value=mock_client):
            result = await send_message(
                to="1234567890@c.us",
                body="Hello",
                openwa_url="http://localhost:3000",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self):
        """Return False when OpenWA is unreachable."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        with patch("gateway.openwa_client.httpx.AsyncClient", return_value=mock_client):
            result = await send_message(
                to="1234567890@c.us",
                body="Hello",
                openwa_url="http://localhost:3000",
            )

        assert result is False
