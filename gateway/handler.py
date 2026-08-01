"""Generate echo responses for incoming messages."""


def build_echo_response(parsed: dict) -> dict:
    """Build an echo response from a parsed message.

    Args:
        parsed: Dict with 'from', 'body', and 'notify_name' from parser.

    Returns:
        Dict with 'to' and 'body' ready for OpenWA send.
    """
    return {
        "to": parsed["from"],
        "body": f"Received: {parsed['body']}",
    }
