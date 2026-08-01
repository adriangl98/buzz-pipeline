"""Unit tests for IntakeManager — multi-turn intake session routing (Ticket 3)."""
import pytest
from faq.manager import IntakeManager


class TestIntakeManager:
    """Session lifecycle: start, route, complete, cancel."""

    def test_start_intake_returns_name_prompt(self):
        mgr = IntakeManager()
        state = mgr.start_intake("phone1@c.us", "en")

        assert state["step"] == "name"
        assert "name" in state["prompt"].lower()

    def test_has_active_after_start(self):
        mgr = IntakeManager()
        assert not mgr.has_active("phone1@c.us")

        mgr.start_intake("phone1@c.us")
        assert mgr.has_active("phone1@c.us")

    def test_full_intake_flow(self):
        mgr = IntakeManager()
        mgr.start_intake("phone1@c.us", "en")

        # Step 1: name
        state = mgr.handle_message("phone1@c.us", "John Smith")
        assert state["step"] == "time_slot"

        # Step 2: time_slot
        state = mgr.handle_message("phone1@c.us", "Friday at 2pm")
        assert state["step"] == "confirm"
        assert "John Smith" in state["prompt"]
        assert "Friday at 2pm" in state["prompt"]

        # Step 3: confirm with yes
        state = mgr.handle_message("phone1@c.us", "yes")
        assert state["step"] == "done"
        assert "saved" in state["prompt"].lower()

        # Session removed after completion
        assert not mgr.has_active("phone1@c.us")

    def test_handle_message_no_active_returns_none(self):
        mgr = IntakeManager()
        result = mgr.handle_message("unknown@c.us", "hello")
        assert result is None

    def test_cancel_during_intake(self):
        mgr = IntakeManager()
        mgr.start_intake("phone1@c.us", "en")
        mgr.handle_message("phone1@c.us", "Alice")

        state = mgr.handle_message("phone1@c.us", "cancel")
        assert state["step"] == "cancelled"
        assert not mgr.has_active("phone1@c.us")

    def test_cancel_at_confirm_step(self):
        mgr = IntakeManager()
        mgr.start_intake("phone1@c.us", "en")
        mgr.handle_message("phone1@c.us", "Bob")
        mgr.handle_message("phone1@c.us", "Monday 9am")

        # At confirm step, "no" cancels
        state = mgr.handle_message("phone1@c.us", "no")
        assert state["step"] == "cancelled"
        assert not mgr.has_active("phone1@c.us")

    def test_spanish_intake_with_confirm(self):
        mgr = IntakeManager()
        mgr.start_intake("phone1@c.us", "es")
        mgr.handle_message("phone1@c.us", "María García")
        mgr.handle_message("phone1@c.us", "viernes a las 3pm")

        state = mgr.handle_message("phone1@c.us", "sí")
        assert state["step"] == "done"
        assert "guardada" in state["prompt"].lower()

    def test_multiple_sessions_independent(self):
        mgr = IntakeManager()
        mgr.start_intake("phone1@c.us", "en")
        mgr.start_intake("phone2@c.us", "es")

        # Phone 1: advance to time_slot
        state1 = mgr.handle_message("phone1@c.us", "Alice")
        assert state1["step"] == "time_slot"

        # Phone 2: advance to time_slot
        state2 = mgr.handle_message("phone2@c.us", "Carlos")
        assert state2["step"] == "time_slot"

        # Both still active
        assert mgr.has_active("phone1@c.us")
        assert mgr.has_active("phone2@c.us")
        assert mgr.active_count() == 2

    def test_active_count(self):
        mgr = IntakeManager()
        assert mgr.active_count() == 0

        mgr.start_intake("a@c.us")
        assert mgr.active_count() == 1

        mgr.start_intake("b@c.us")
        assert mgr.active_count() == 2

        mgr.handle_message("a@c.us", "cancel")
        assert mgr.active_count() == 1
