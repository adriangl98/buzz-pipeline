"""Parse OpenWA webhook payloads into structured message objects."""


def parse_webhook(payload: dict) -> dict:
    """Parse an OpenWA webhook payload and extract message fields.

    Args:
        payload: Raw webhook JSON from OpenWA.

    Returns:
        dict with keys: from, body, notify_name.

    Raises:
        ValueError: If event is not 'message' or required fields are missing.
    """
    event = payload.get("event")
    if event != "message":
        raise ValueError(f"Unsupported event: {event}")

    data = payload.get("data", {})

    required = ["from", "body", "notifyName"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return {
        "from": data["from"],
        "body": data["body"],
        "notify_name": data["notifyName"],
    }
