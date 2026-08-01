"""Intake manager — tracks active new-patient intake sessions per phone.

Routes multi-turn intake conversations: start → name → time_slot → confirm → done.
"""
from faq.intake import IntakeForm


class IntakeManager:
    """Manages active intake sessions for the gateway.

    One active intake per phone at a time. Completed/cancelled
    intakes are removed and the collected data is returned.
    """

    def __init__(self):
        self._sessions: dict[str, IntakeForm] = {}

    def start_intake(self, phone: str, language: str = "en") -> dict:
        """Begin a new intake flow for a phone.

        Returns the first prompt (step='name').
        """
        form = IntakeForm(phone=phone, language=language)
        self._sessions[phone] = form
        return form.start()

    def has_active(self, phone: str) -> bool:
        """Check if a phone has an active intake session."""
        return phone in self._sessions

    def handle_message(self, phone: str, message: str) -> dict | None:
        """Route a message through the active intake flow.

        Returns the next state dict, or None if no active intake.
        Detects cancel keywords ('cancel', 'cancelar', 'no')
        and confirm keywords ('yes', 'sí', 'si', 'ok') at the
        confirm step.
        """
        if phone not in self._sessions:
            return None

        form = self._sessions[phone]
        lower = message.lower().strip()

        # Check for cancellation at any step
        if lower in ("cancel", "cancelar", "no", "stop"):
            state = form.cancel()
            del self._sessions[phone]
            return state

        # At confirm step, check for yes/no
        current_step = form.STEPS[form._step_index] if form._step_index < len(form.STEPS) else "done"
        if current_step == "confirm":
            if lower in ("yes", "sí", "si", "ok", "confirm"):
                state = form.confirm()
                del self._sessions[phone]
                return state
            if lower in ("no", "cancel", "cancelar"):
                state = form.cancel()
                del self._sessions[phone]
                return state

        # Normal advance
        return form.advance(message)

    def active_count(self) -> int:
        """Return number of active intake sessions."""
        return len(self._sessions)
