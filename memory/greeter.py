"""Patient greeting service — personalizes responses based on history."""
from memory.store import PatientStore


class PatientGreeter:
    """Generate personalized greetings using patient history."""

    def __init__(self, store: PatientStore):
        self._store = store

    def greet(self, phone: str, incoming_message: str = "") -> str:
        """Generate an appropriate greeting for a patient.

        Args:
            phone: WhatsApp phone number of the sender.
            incoming_message: The patient's message (for language detection).

        Returns:
            A greeting string in the appropriate language.
        """
        patient = self._store.get_by_phone(phone)
        lang = self._detect_language(incoming_message)

        if patient is None:
            return self._new_patient_greeting(lang)

        return self._returning_patient_greeting(patient, lang)

    def greet_with_verification(
        self, phone: str, incoming_message: str = ""
    ) -> dict:
        """Greet and check for identity verification needs.

        Returns:
            dict with keys: greeting, verified, suggested_match (or None).
        """
        patient = self._store.get_by_phone(phone)
        if patient is not None:
            return {
                "greeting": self.greet(phone, incoming_message),
                "verified": True,
                "suggested_match": None,
            }

        # Unknown phone — check if name appears in the message
        name = self._extract_name(incoming_message)
        if name:
            matches = self._store.find_by_name(name)
            if matches:
                lang = self._detect_language(incoming_message)
                return {
                    "greeting": self._verification_greeting(matches[0], lang),
                    "verified": False,
                    "suggested_match": matches[0],
                }

        return {
            "greeting": self.greet(phone, incoming_message),
            "verified": True,  # New patient, no conflict
            "suggested_match": None,
        }

    def verify_identity(self, new_phone: str, existing_phone: str) -> bool:
        """Link a new phone to an existing patient after verification."""
        return self._store.link_phone(
            existing_phone=existing_phone,
            new_phone=new_phone,
        )

    # ── private helpers ──────────────────────────────────────────────

    def _returning_patient_greeting(self, patient: dict, lang: str) -> str:
        name = patient["name"]
        first_name = name.split()[0]
        last_visit = patient["last_visit"]

        if lang == "es":
            return (
                f"¡Bienvenida de nuevo, {first_name}! "
                f"Veo que su última visita fue el {last_visit}. "
                f"¿En qué puedo ayudarle hoy?"
            )
        return (
            f"Welcome back, {first_name}! "
            f"I see your last visit was on {last_visit}. "
            f"How can I help you today?"
        )

    def _new_patient_greeting(self, lang: str) -> str:
        if lang == "es":
            return (
                "¡Hola! Bienvenido a Laredo Dental. "
                "¿Es su primera visita con nosotros? "
                "¿En qué puedo ayudarle?"
            )
        return (
            "Hello! Welcome to Laredo Dental. "
            "Is this your first visit with us? "
            "How can I help you?"
        )

    def _verification_greeting(self, patient: dict, lang: str) -> str:
        name = patient["name"]
        first_name = name.split()[0]
        if lang == "es":
            return (
                f"¿Eres {first_name}? "
                f"Veo que has enviado un mensaje desde un número diferente. "
                f"¿Puedes confirmar tu identidad?"
            )
        return (
            f"Is this {first_name}? "
            f"I see you're messaging from a different number. "
            f"Can you confirm your identity?"
        )

    @staticmethod
    def _detect_language(message: str) -> str:
        """Simple language detection: check for Spanish markers."""
        if not message:
            return "en"
        spanish_markers = [
            "hola", "gracias", "cita", "por favor", "¿", "ñ",
            "buenos", "buenas", "tardes", "días",
        ]
        lower = message.lower()
        for marker in spanish_markers:
            if marker in lower:
                return "es"
        return "en"

    @staticmethod
    def _extract_name(message: str) -> str | None:
        """Attempt to extract a name from the message."""
        soy_prefixes = ["soy ", "me llamo ", "mi nombre es "]
        lower = message.lower()
        for prefix in soy_prefixes:
            if prefix in lower:
                idx = lower.index(prefix) + len(prefix)
                rest = message[idx:].strip().rstrip(".,!?¿¡")
                # Take first word or two as the name
                parts = rest.split()
                if parts:
                    return " ".join(parts[:2]).title()
        return None
