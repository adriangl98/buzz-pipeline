"""Detect when to escalate a patient message to the dental office owner.

Escalation triggers:
- medical_advice — treatment questions, diagnoses
- pricing — cost questions, payment
- appointment_booking — actual booking (not inquiries)
- unknown — FAQ didn't match, agent is uncertain
"""


class EscalationDetector:
    """Classify whether a message needs human (owner) intervention."""

    MEDICAL_KEYWORDS = {
        "en": [
            "root canal", "extraction", "surgery", "implant", "pain",
            "infection", "swollen", "bleeding", "cavity", "crown",
            "need a", "do i need", "should i get", "treatment",
            "diagnosis", "x-ray", "prescription", "antibiotic",
            "emergency", "broken tooth", "chipped", "abscess",
        ],
        "es": [
            "endodoncia", "extracción", "extraccion", "cirugía", "cirugia",
            "implante", "dolor", "infección", "infeccion", "inflamado",
            "sangrado", "caries", "corona", "necesito una", "tratamiento",
            "diagnóstico", "diagnostico", "radiografía", "radiografia",
            "receta", "antibiótico", "antibiotico", "emergencia",
            "diente roto", "absceso",
        ],
    }

    PRICING_KEYWORDS = {
        "en": [
            "how much", "cost", "price", "expensive", "cheap",
            "insurance cover", "payment plan", "pay for", "bill",
            "covered by", "discount", "fee",
        ],
        "es": [
            "cuánto cuesta", "cuanto cuesta", "precio", "costo",
            "caro", "barato", "cubre el seguro", "plan de pago",
            "pagar", "factura", "descuento", "cuota",
        ],
    }

    BOOKING_KEYWORDS = {
        "en": [
            "book an appointment", "schedule", "make an appointment",
            "set up", "reserve", "confirm appointment", "coming in",
        ],
        "es": [
            "agendar cita", "hacer cita", "reservar", "confirmar cita",
            "programar cita", "pedir cita",
        ],
    }

    def should_escalate(self, message: str, faq_match: bool = True) -> dict:
        """Check whether a message should be escalated.

        Args:
            message: The patient's message text.
            faq_match: Whether the FAQ module found a match (default True).

        Returns:
            dict with 'escalate' (bool) and 'reason' (str).
        """
        lower = message.lower()

        # Check medical advice — highest priority (must escalate)
        for lang_kw in self.MEDICAL_KEYWORDS.values():
            for kw in lang_kw:
                if kw in lower:
                    return {"escalate": True, "reason": "medical_advice"}

        # Check pricing questions
        for lang_kw in self.PRICING_KEYWORDS.values():
            for kw in lang_kw:
                if kw in lower:
                    return {"escalate": True, "reason": "pricing"}

        # Check appointment booking (not just inquiries)
        for lang_kw in self.BOOKING_KEYWORDS.values():
            for kw in lang_kw:
                if kw in lower:
                    return {"escalate": True, "reason": "appointment_booking"}

        # FAQ didn't match → escalate as unknown
        if not faq_match:
            return {"escalate": True, "reason": "unknown"}

        return {"escalate": False, "reason": ""}

    def build_context(
        self,
        patient_name: str,
        phone: str,
        question: str,
        reason: str,
    ) -> str:
        """Build a human-readable escalation context message.

        Args:
            patient_name: Patient's name.
            phone: Patient's WhatsApp phone number.
            question: The patient's original question.
            reason: Escalation reason code.

        Returns:
            Formatted context string for the owner.
        """
        reason_labels = {
            "medical_advice": "Medical advice requested",
            "pricing": "Pricing question",
            "appointment_booking": "Appointment booking",
            "unknown": "Unknown question — I'm not sure how to answer",
        }
        label = reason_labels.get(reason, reason)

        return (
            f"🚨 ESCALATION: {label}\n"
            f"Patient: {patient_name}\n"
            f"Phone: {phone}\n"
            f"Question: {question}\n\n"
            f"Please reply and I'll relay your response to the patient."
        )
