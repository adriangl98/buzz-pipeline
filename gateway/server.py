"""Unified Hermes Gateway — pilot-ready."""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from gateway.parser import parse_webhook
from gateway.openwa_client import send_message
from memory.store import PatientStore
from memory.greeter import PatientGreeter
from faq.knowledge import FAQ
from escalation.engine import EscalationEngine

OPENWA_URL = os.environ.get("OPENWA_URL", "http://localhost:3000")


def create_app(
    store: PatientStore | None = None,
    greeter: PatientGreeter | None = None,
    faq: FAQ | None = None,
    escalation: EscalationEngine | None = None,
) -> FastAPI:
    store = store or PatientStore()
    greeter = greeter or PatientGreeter(store)
    faq = faq or FAQ()
    escalation = escalation or EscalationEngine()

    app = FastAPI(title="Hermes Gateway — Pilot")

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "patients": store.count(),
            "faq_topics": len(faq.ANSWERS),
            "pending_escalations": escalation.pending_count,
        }

    @app.post("/webhook")
    async def webhook(request: Request):
        payload = await request.json()
        try:
            parsed = parse_webhook(payload)
        except ValueError as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})

        phone = parsed["from"]
        body = parsed["body"]
        name = parsed["notify_name"]

        greeting = greeter.greet(phone, body)
        faq_answer = faq.ask(body)

        if faq_answer is not None:
            response_text = f"{greeting}\n\n{faq_answer}"
        else:
            esc = escalation.escalate(phone, name, body)
            response_text = (
                f"{greeting}\n\nI've sent your question to our team. "
                f"They'll get back to you within 24 hours."
            )

        success = await send_message(to=phone, body=response_text, openwa_url=OPENWA_URL)
        if success:
            return {"status": "ok"}
        return JSONResponse(status_code=502, content={"detail": "Failed to send via OpenWA"})

    @app.post("/escalation/resolve")
    async def resolve_escalation(request: Request):
        data = await request.json()
        patient_phone = data.get("patient_phone")
        owner_response = data.get("response")
        if not patient_phone or not owner_response:
            return JSONResponse(status_code=400, content={"detail": "Missing fields"})
        esc = escalation.resolve(patient_phone, owner_response)
        if esc is None:
            return JSONResponse(status_code=404, content={"detail": "No pending escalation"})
        relay_text = escalation.relay_to_patient(esc)
        success = await send_message(to=patient_phone, body=relay_text, openwa_url=OPENWA_URL)
        if success:
            return {"status": "ok", "relayed": relay_text}
        return JSONResponse(status_code=502, content={"detail": "Failed to relay"})

    return app


app = create_app()
