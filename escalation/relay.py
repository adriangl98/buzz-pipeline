"""SMS relay — sends alerts to owner and relays responses back to patients."""
from gateway.openwa_client import send_message


class SMSRelay:
    """Relay escalation messages between the agent and the dental office owner."""

    MAX_SMS_LENGTH = 320

    def __init__(self, owner_phone: str):
        self._owner_phone = owner_phone

    def build_alert(
        self,
        patient_name: str,
        patient_phone: str,
        question: str,
        reason: str,
    ) -> str:
        """Build a compact SMS alert for the owner.

        Args:
            patient_name: Patient's name.
            patient_phone: Patient's WhatsApp phone.
            question: The original question.
            reason: Escalation reason code.

        Returns:
            SMS-friendly alert string (under 320 chars).
        """
        reason_labels = {
            "medical_advice": "Medical Q",
            "pricing": "Pricing Q",
            "appointment_booking": "Booking",
            "unknown": "Unknown Q",
        }
        label = reason_labels.get(reason, reason)

        message = (
            f"[{label}] {patient_name} ({patient_phone})\n"
            f"Q: {question}\n"
            f"Reply to relay to patient."
        )

        # Trim if too long
        if len(message) > self.MAX_SMS_LENGTH:
            message = message[: self.MAX_SMS_LENGTH - 3] + "..."

        return message

    async def alert_owner(
        self,
        patient_name: str,
        patient_phone: str,
        question: str,
        reason: str,
    ) -> bool:
        """Send an escalation alert to the owner.

        Args:
            patient_name: Patient's name.
            patient_phone: Patient's WhatsApp phone.
            question: The original question.
            reason: Escalation reason code.

        Returns:
            True if sent successfully.
        """
        alert = self.build_alert(patient_name, patient_phone, question, reason)
        return await send_message(
            to=self._owner_phone,
            body=alert,
        )

    async def relay_to_patient(
        self,
        patient_phone: str,
        owner_reply: str,
    ) -> bool:
        """Relay the owner's reply back to the patient.

        Args:
            patient_phone: Original patient's WhatsApp phone.
            owner_reply: The owner's response text.

        Returns:
            True if sent successfully.
        """
        return await send_message(
            to=patient_phone,
            body=owner_reply,
        )
