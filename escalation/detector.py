"""Escalation detector: determine when to escalate to human owner.

Rules:
- Medical advice → escalate
- Pricing → escalate
- Booking → escalate (no API integration for MVP)
- FAQ questions → do NOT escalate
"""
import re


class EscalationDetector:
    """Keyword-based escalation detection for bilingual input."""

    ESCALATE_PATTERNS = [
        # Medical advice (EN + ES)
        r"\b(need|necesito|should|debo|prescribe|recetar|antibiotic|antibiótico)\b",
        r"\b(infection|infección|pain|dolor|swelling|hinchazón|serious|grave)\b",
        r"\b(medication|medicamento|medicine|medicina|pill|pastilla)\b",
        r"\b(root canal|endodoncia|extraction|extracción|surgery|cirugía)\b",
        # Pricing (EN + ES)
        r"\b(how much|cuánto|cuesta|cost|price|precio|charge|cobran)\b",
        r"\b(afford|pagar|payment plan|plan de pago|expensive|caro)\b",
        # Booking (EN + ES — no API, must escalate)
        r"\b(book|reservar|schedule|agendar|appointment|cita|make an? appointment)\b",
        r"\b(for (monday|tuesday|wednesday|thursday|friday|lunes|martes|miércoles|jueves|viernes))\b",
        r"\b(at \d|a las \d|tomorrow|mañana|next week|próxima semana)\b",
    ]

    FAQ_INDICATORS = [
        # Questions our FAQ handles (should NOT escalate)
        r"\b(hours?|horarios?|open|abierto|close|cerrado|schedule)\b",
        r"\b(where|dónde|located|ubicado|address|dirección|parking|estacionamiento)\b",
        r"\b(insurance|seguro|aseguranza|accept|aceptan|plan|coverage|cobertura)\b",
        r"\b(services?|servicio|offer|ofrecen|cleaning|limpieza|filling|relleno)\b",
        r"\b(new patient|nuevo paciente|first time|primera vez|first visit)\b",
    ]

    def should_escalate(self, question: str) -> dict:
        """Determine if a question should be escalated to owner.

        Returns:
            dict with 'escalate' (bool) and 'reason' (str).
        """
        lower = question.lower()

        # Check escalation patterns first
        for pattern in self.ESCALATE_PATTERNS:
            if re.search(pattern, lower):
                return {"escalate": True, "reason": f"Matched escalation pattern: {pattern}"}

        # FAQ indicators that block escalation
        for pattern in self.FAQ_INDICATORS:
            if re.search(pattern, lower):
                return {"escalate": False, "reason": "FAQ-covered question"}

        # Default: escalate unknown questions
        return {"escalate": True, "reason": "No FAQ match — escalate for safety"}
