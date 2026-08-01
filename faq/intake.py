"""New patient intake form — multi-step data collection."""


class IntakeForm:
    """Multi-step form to collect new patient information.

    Steps: start → name → time_slot → confirm → done
    """

    STEPS = ["name", "time_slot", "confirm", "done"]

    PROMPTS = {
        "name": {
            "en": "Great! To get started, what's your full name?",
            "es": "¡Excelente! Para comenzar, ¿cuál es su nombre completo?",
        },
        "time_slot": {
            "en": "Thanks! What day and time works best for your appointment?",
            "es": "¡Gracias! ¿Qué día y hora le funciona mejor para su cita?",
        },
        "confirm": {
            "en": "Got it! I have: {name}, phone {phone}, preferred time: {time_slot}. "
            "Our staff will call you within 24 hours to confirm. Is that correct? (yes/no)",
            "es": "¡Entendido! Tengo: {name}, teléfono {phone}, horario preferido: {time_slot}. "
            "Nuestro personal le llamará dentro de 24 horas para confirmar. ¿Es correcto? (sí/no)",
        },
        "done": {
            "en": "Perfect! Your information has been saved. Our staff will call you within 24 hours to confirm your appointment. Thank you for choosing Laredo Dental!",
            "es": "¡Perfecto! Su información ha sido guardada. Nuestro personal le llamará dentro de 24 horas para confirmar su cita. ¡Gracias por elegir Laredo Dental!",
        },
        "cancelled": {
            "en": "No problem! Your intake has been cancelled. Let us know when you're ready to reschedule.",
            "es": "¡No hay problema! Su registro ha sido cancelado. Avísenos cuando esté listo para reprogramar.",
        },
    }

    def __init__(self, phone: str, language: str = "en"):
        self._phone = phone
        self._language = language
        self._data: dict[str, str] = {"phone": phone}
        self._step_index = 0

    def start(self) -> dict:
        """Begin the intake flow. Returns the first prompt."""
        self._step_index = 0
        return self._state("name")

    def advance(self, response: str) -> dict:
        """Advance to the next step with the user's response.

        Args:
            response: The user's answer to the current prompt.

        Returns:
            dict with step, prompt, and accumulated data.
        """
        current = self.STEPS[self._step_index]

        if current == "name":
            self._data["name"] = response.strip()
            self._step_index = 1
            return self._state("time_slot")

        if current == "time_slot":
            self._data["time_slot"] = response.strip()
            self._step_index = 2
            prompt = self.PROMPTS["confirm"][self._language].format(**self._data)
            return {
                "step": "confirm",
                "prompt": prompt,
                "data": dict(self._data),
            }

        return self._state(current)

    def confirm(self) -> dict:
        """Confirm the intake and mark as done."""
        self._step_index = 3
        return self._state("done")

    def cancel(self) -> dict:
        """Cancel the intake flow."""
        return {
            "step": "cancelled",
            "prompt": self.PROMPTS["cancelled"][self._language],
            "data": dict(self._data),
        }

    def _state(self, step: str) -> dict:
        prompt_key = "confirm" if step == "confirm" else step
        if step == "confirm":
            prompt = self.PROMPTS["confirm"][self._language].format(**self._data)
        elif step == "done":
            prompt = self.PROMPTS["done"][self._language]
        else:
            prompt = self.PROMPTS.get(prompt_key, {}).get(self._language, "")
        return {
            "step": step,
            "prompt": prompt,
            "data": dict(self._data),
        }
