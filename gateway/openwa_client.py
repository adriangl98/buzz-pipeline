"""Send messages to WhatsApp via OpenWA REST API."""
import httpx


async def send_message(
    to: str,
    body: str,
    openwa_url: str = "http://localhost:3000",
) -> bool:
    """Send a text message via OpenWA.

    Args:
        to: WhatsApp chat ID (e.g., '1234567890@c.us').
        body: Message text to send.
        openwa_url: Base URL of the OpenWA instance.

    Returns:
        True if sent successfully, False on any error.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{openwa_url}/api/sendText",
                json={"chatId": to, "text": body},
                timeout=5.0,
            )
            return response.status_code == 200
    except httpx.TransportError:
        return False
