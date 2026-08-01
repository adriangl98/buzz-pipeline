"""Escalation engine: route uncertain queries to human owner."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Escalation:
    patient_name: str
    patient_phone: str
    question: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved: bool = False
    owner_response: str | None = None


class EscalationEngine:
    def __init__(self):
        self._pending: dict[str, Escalation] = {}

    def escalate(self, patient_phone: str, patient_name: str, question: str) -> Escalation:
        esc = Escalation(patient_name=patient_name, patient_phone=patient_phone, question=question)
        self._pending[patient_phone] = esc
        return esc

    def owner_sms_text(self, escalation: Escalation) -> str:
        return (
            f"Patient: {escalation.patient_name}\n"
            f"Question: {escalation.question}\n"
            f"Phone: {escalation.patient_phone}\n"
            f"I don't know the answer. Reply to this message to respond."
        )

    def resolve(self, patient_phone: str, owner_response: str) -> Escalation | None:
        esc = self._pending.pop(patient_phone, None)
        if esc is None:
            return None
        esc.resolved = True
        esc.owner_response = owner_response
        return esc

    def relay_to_patient(self, escalation: Escalation) -> str:
        return f"Our staff says: {escalation.owner_response}\n\n— Sent by the Laredo Dental team"

    def get_pending(self, patient_phone: str) -> Escalation | None:
        return self._pending.get(patient_phone)

    @property
    def pending_count(self) -> int:
        return len(self._pending)
