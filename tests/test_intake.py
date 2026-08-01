"""Unit tests for IntakeForm — new patient multi-step data collection (Ticket 3).

Tests the full intake flow: start → name → time_slot → confirm → done,
bilingual support, cancellation, and data integrity.
"""
import pytest
from faq.intake import IntakeForm


class TestIntakeFlow:
    """Full intake lifecycle: start through done."""

    def test_start_returns_name_prompt(self):
        form = IntakeForm(phone="521234567890@c.us", language="en")
        state = form.start()

        assert state["step"] == "name"
        assert "name" in state["prompt"].lower()
        assert state["data"]["phone"] == "521234567890@c.us"

    def test_full_english_flow(self):
        form = IntakeForm(phone="1234567890@c.us", language="en")

        # Step 1: name
        state = form.start()
        assert state["step"] == "name"

        # Step 2: time_slot
        state = form.advance("John Smith")
        assert state["step"] == "time_slot"
        assert "day" in state["prompt"].lower() or "time" in state["prompt"].lower()

        # Step 3: confirm
        state = form.advance("Friday at 2pm")
        assert state["step"] == "confirm"
        assert "John Smith" in state["prompt"]
        assert "Friday at 2pm" in state["prompt"]
        assert "1234567890@c.us" in state["prompt"]
        assert "24 hours" in state["prompt"]

        # Step 4: done
        state = form.confirm()
        assert state["step"] == "done"
        assert "saved" in state["prompt"].lower() or "call you" in state["prompt"].lower()

    def test_full_spanish_flow(self):
        form = IntakeForm(phone="521234567890@c.us", language="es")

        form.start()
        state = form.advance("María García")
        assert "María García" in state["data"]["name"]

        state = form.advance("viernes a las 2pm")
        assert state["step"] == "confirm"
        assert "María García" in state["prompt"]
        assert "viernes" in state["prompt"].lower()

        state = form.confirm()
        assert state["step"] == "done"
        assert "guardada" in state["prompt"].lower()

    def test_data_collected_completely(self):
        """All fields (name, phone, time_slot) are collected."""
        form = IntakeForm(phone="1234567890@c.us", language="en")
        form.start()
        form.advance("Alice Jones")
        state = form.advance("Monday 10am")

        assert state["data"]["name"] == "Alice Jones"
        assert state["data"]["phone"] == "1234567890@c.us"
        assert state["data"]["time_slot"] == "Monday 10am"

    def test_start_resets_flow(self):
        """Calling start() again resets the intake flow."""
        form = IntakeForm(phone="x@c.us", language="en")
        form.start()
        form.advance("Bob")
        form.advance("Tuesday 3pm")

        # Restart
        state = form.start()
        assert state["step"] == "name"
        assert "name" in state["prompt"].lower()


class TestIntakeCancellation:
    """User can cancel the intake flow."""

    def test_cancel_returns_cancelled_prompt(self):
        form = IntakeForm(phone="x@c.us", language="en")
        state = form.cancel()

        assert state["step"] == "cancelled"
        assert "cancelled" in state["prompt"].lower()

    def test_cancel_spanish(self):
        form = IntakeForm(phone="x@c.us", language="es")
        state = form.cancel()

        assert state["step"] == "cancelled"
        assert "cancelado" in state["prompt"].lower()

    def test_cancel_preserves_collected_data(self):
        """Cancellation preserves what was already collected."""
        form = IntakeForm(phone="1234567890@c.us", language="en")
        form.start()
        form.advance("Alice")
        state = form.cancel()

        assert state["data"]["name"] == "Alice"
        assert state["data"]["phone"] == "1234567890@c.us"


class TestIntakeDataIntegrity:
    """Collected data is consistent throughout the flow."""

    def test_phone_persisted_through_flow(self):
        form = IntakeForm(phone="phone@c.us", language="en")
        form.start()
        s1 = form.advance("Test User")
        s2 = form.advance("Tomorrow")

        assert s1["data"]["phone"] == "phone@c.us"
        assert s2["data"]["phone"] == "phone@c.us"
        assert s2["data"]["name"] == "Test User"
        assert s2["data"]["time_slot"] == "Tomorrow"

    def test_name_trimmed(self):
        """Names with extra whitespace are trimmed."""
        form = IntakeForm(phone="x@c.us", language="en")
        form.start()
        state = form.advance("  John   Doe  ")

        assert state["data"]["name"] == "John   Doe"
