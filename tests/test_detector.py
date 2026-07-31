"""Tests for escalation detector."""
import pytest
from escalation.detector import EscalationDetector


class TestEscalationDetector:
    """Detect when to escalate a patient message to the owner."""

    def test_escalates_medical_advice_question(self):
        """Block and escalate any medical advice questions."""
        detector = EscalationDetector()

        result = detector.should_escalate("Do I need a root canal or extraction?")

        assert result["escalate"] is True
        assert result["reason"] == "medical_advice"

    def test_escalates_price_confirmation(self):
        """Escalate appointment price confirmations."""
        detector = EscalationDetector()

        result = detector.should_escalate("How much does a cleaning cost?")

        assert result["escalate"] is True
        assert result["reason"] == "pricing"

    def test_escalates_appointment_booking(self):
        """Escalate actual appointment booking (not just inquiries)."""
        detector = EscalationDetector()

        result = detector.should_escalate("I want to book an appointment for Friday at 2pm")

        assert result["escalate"] is True
        assert result["reason"] == "appointment_booking"

    def test_does_not_escalate_faq_hours(self):
        """FAQ questions about hours should NOT escalate."""
        detector = EscalationDetector()

        result = detector.should_escalate("What are your office hours?")

        assert result["escalate"] is False

    def test_does_not_escalate_faq_location(self):
        """FAQ location questions should NOT escalate."""
        detector = EscalationDetector()

        result = detector.should_escalate("Where are you located?")

        assert result["escalate"] is False

    def test_escalates_unknown_questions(self):
        """Questions not in FAQ that the agent can't answer should escalate."""
        detector = EscalationDetector()

        result = detector.should_escalate(
            "Can you recommend a good toothpaste brand for sensitive teeth?",
            faq_match=False,
        )

        assert result["escalate"] is True
        assert result["reason"] == "unknown"

    def test_spanish_medical_escalation(self):
        """Spanish medical questions also escalate."""
        detector = EscalationDetector()

        result = detector.should_escalate("¿Necesito una endodoncia o extracción?")

        assert result["escalate"] is True
        assert result["reason"] == "medical_advice"

    def test_builds_escalation_context(self):
        """Build a context message with patient info for the owner."""
        detector = EscalationDetector()

        context = detector.build_context(
            patient_name="María García",
            phone="521234567890@c.us",
            question="¿Necesito una endodoncia?",
            reason="medical_advice",
        )

        assert "María García" in context
        assert "521234567890" in context
        assert "endodoncia" in context
        assert "medical" in context.lower()
