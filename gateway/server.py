"""FastAPI gateway server with FAQ knowledge base."""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from faq.knowledge import FAQ
from gateway.openwa_client import send_message

OPENWA_URL = os.environ.get("OPENWA_URL", "http://localhost:3000")


def create_app(faq: FAQ | None = None) -> FastAPI:
    """Create the gateway app with FAQ injection.

    Args:
        faq: FAQ instance (creates default if None).

    Returns:
        Configured FastAPI application.
    """
    if faq is None:
        faq = FAQ()

    app = FastAPI(title="Hermes Gateway — FAQ")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "topics": len(faq.ANSWERS)}

    @app.post("/webhook")
    async def webhook(request: Request):
        payload = await request.json()

        event = payload.get("event")
        if event != "message":
            return JSONResponse(
                status_code=400,
                content={"detail": f"Unsupported event: {event}"},
            )

        data = payload.get("data", {})
        phone = data.get("from", "")
        body = data.get("body", "")

        if not phone or not body:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing required fields: from, body"},
            )

        # Try FAQ first
        answer = faq.ask(body)

        # Fallback: echo with uncertainty note
        if answer is None:
            answer = (
                f"Received: {body}\n\n"
                "I'm not sure how to answer that. Our staff can help — "
                "they'll get back to you within 24 hours."
            )

        success = await send_message(
            to=phone,
            body=answer,
            openwa_url=OPENWA_URL,
        )

        if success:
            return {"status": "ok"}

        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to send message via OpenWA"},
        )

    return app


app = create_app()
