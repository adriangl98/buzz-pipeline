"""FastAPI server: receives OpenWA webhooks, echoes back responses."""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from gateway.parser import parse_webhook
from gateway.handler import build_echo_response
from gateway.openwa_client import send_message

app = FastAPI(title="Hermes Gateway")

OPENWA_URL = os.environ.get("OPENWA_URL", "http://localhost:3000")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    try:
        parsed = parse_webhook(payload)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

    response = build_echo_response(parsed)

    success = await send_message(
        to=response["to"],
        body=response["body"],
        openwa_url=OPENWA_URL,
    )

    if success:
        return {"status": "ok"}

    return JSONResponse(
        status_code=502,
        content={"detail": "Failed to send message via OpenWA"},
    )
