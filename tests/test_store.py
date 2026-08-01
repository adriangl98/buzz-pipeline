"""Unit tests for PatientStore — Honcho patient memory (Ticket 2).

Tests patient storage, retrieval, alias resolution, identity verification,
and NEW: conversation tracking (count + history).
"""
import pytest
from datetime import date

from memory.store import PatientStore


class TestPatientStore:
    """Core CRUD: add, get, update, count."""

    def test_adds_and_retrieves_patient(self):
        """Patient added by phone is retrievable."""
        store = PatientStore()
        store.add("521234567890@c.us", "María García", date(2026, 7, 15))

        record = store.get_by_phone("521234567890@c.us")

        assert record is not None
        assert record["name"] == "María García"
        assert record["phone"] == "521234567890@c.us"
        assert record["last_visit"] == "2026-07-15"

    def test_updates_last_visit(self):
        """update_last_visit changes the visit date for an existing patient."""
        store = PatientStore()
        store.add("521234567890@c.us", "María García", date(2026, 7, 15))

        updated = store.update_last_visit("521234567890@c.us", date(2026, 8, 1))

        assert updated is not None
        assert updated["last_visit"] == "2026-08-01"
        assert store.get_by_phone("521234567890@c.us")["last_visit"] == "2026-08-01"

    def test_update_last_visit_nonexistent_returns_none(self):
        """Updating a patient that doesn't exist returns None."""
        store = PatientStore()

        result = store.update_last_visit("521234567890@c.us", date(2026, 8, 1))

        assert result is None

    def test_count_reflects_unique_patients(self):
        """Count returns the number of unique patients (not aliases)."""
        store = PatientStore()

        assert store.count() == 0

        store.add("phone1@c.us", "Alice", date(2026, 1, 1))
        assert store.count() == 1

        store.add("phone2@c.us", "Bob", date(2026, 1, 1))
        assert store.count() == 2

        store.link_phone("phone1@c.us", "phone1b@c.us")
        assert store.count() == 2  # alias doesn't increase count


class TestAliasResolution:
    """Phone number linking and alias chain resolution."""

    def test_links_alternate_phone(self):
        """Linking a new phone to an existing patient makes both resolve."""
        store = PatientStore()
        store.add("521234567890@c.us", "María García", date(2026, 7, 15))

        result = store.link_phone("521234567890@c.us", "521234999999@c.us")

        assert result is True
        assert store.get_by_phone("521234999999@c.us")["name"] == "María García"

    def test_resolves_alias_chain(self):
        """Alias chains (A→B→C) resolve to the canonical phone."""
        store = PatientStore()
        store.add("a@c.us", "Alice", date(2026, 1, 1))
        store.link_phone("a@c.us", "b@c.us")
        store.link_phone("a@c.us", "c@c.us")
        store.link_phone("c@c.us", "d@c.us")

        record = store.get_by_phone("d@c.us")

        assert record is not None
        assert record["phone"] == "a@c.us"
        assert record["name"] == "Alice"

    def test_link_nonexistent_phone_fails(self):
        """Linking from a phone that doesn't exist returns False."""
        store = PatientStore()

        result = store.link_phone("does-not-exist@c.us", "new@c.us")

        assert result is False


class TestFindByName:
    """Name-based patient lookup for identity verification."""

    def test_finds_by_name_case_insensitive(self):
        """find_by_name matches regardless of case."""
        store = PatientStore()
        store.add("phone1@c.us", "María García", date(2026, 7, 15))

        matches = store.find_by_name("maría garcía")

        assert len(matches) == 1
        assert matches[0]["phone"] == "phone1@c.us"

    def test_find_by_name_returns_multiple(self):
        """Multiple patients with same name all returned."""
        store = PatientStore()
        store.add("phone1@c.us", "John Smith", date(2026, 1, 1))
        store.add("phone2@c.us", "John Smith", date(2026, 2, 1))

        matches = store.find_by_name("john smith")

        assert len(matches) == 2

    def test_find_by_name_no_match_returns_empty(self):
        """No matching name returns empty list."""
        store = PatientStore()
        store.add("phone1@c.us", "Alice", date(2026, 1, 1))

        matches = store.find_by_name("Bob")

        assert matches == []


class TestScaleTo20Patients:
    """Scale requirement from acceptance criteria."""

    def test_stores_20_patients(self):
        """PatientStore handles 20 patients without issues."""
        store = PatientStore()
        for i in range(20):
            store.add(
                f"phone{i}@c.us",
                f"Patient {i}",
                date(2026, 7, (i % 28) + 1),
            )

        assert store.count() == 20
        for i in range(20):
            record = store.get_by_phone(f"phone{i}@c.us")
            assert record is not None
            assert record["name"] == f"Patient {i}"


class TestConversationTracking:
    """NEW for Ticket 2: per-patient conversation count and history."""

    def test_tracks_conversation_count(self):
        """Each add_conversation increments the patient's conversation count."""
        store = PatientStore()
        store.add("phone1@c.us", "Alice", date(2026, 7, 1))

        assert store.get_conversation_count("phone1@c.us") == 0

        store.add_conversation("phone1@c.us", "Hi, I need an appointment")
        assert store.get_conversation_count("phone1@c.us") == 1

        store.add_conversation("phone1@c.us", "What time do you open?")
        assert store.get_conversation_count("phone1@c.us") == 2

        store.add_conversation("phone1@c.us", "Thank you!")
        assert store.get_conversation_count("phone1@c.us") == 3

    def test_add_conversation_stores_message_history(self):
        """Conversation messages are stored and retrievable."""
        store = PatientStore()
        store.add("phone1@c.us", "Alice", date(2026, 7, 1))

        store.add_conversation("phone1@c.us", "Hi, I need an appointment")
        store.add_conversation("phone1@c.us", "What time do you open?")

        history = store.get_conversation_history("phone1@c.us")

        assert len(history) == 2
        assert history[0]["message"] == "Hi, I need an appointment"
        assert history[1]["message"] == "What time do you open?"
        assert "timestamp" in history[0]

    def test_get_conversation_count_unknown_patient_returns_0(self):
        """Asking for conversation count of unknown patient returns 0."""
        store = PatientStore()

        count = store.get_conversation_count("unknown@c.us")

        assert count == 0

    def test_get_conversation_history_unknown_patient_returns_empty(self):
        """Asking for history of unknown patient returns empty list."""
        store = PatientStore()

        history = store.get_conversation_history("unknown@c.us")

        assert history == []

    def test_conversation_count_works_through_aliases(self):
        """Conversation tracking resolves through alias chain."""
        store = PatientStore()
        store.add("phone1@c.us", "Alice", date(2026, 7, 1))
        store.link_phone("phone1@c.us", "phone1b@c.us")

        store.add_conversation("phone1@c.us", "Hello")
        store.add_conversation("phone1b@c.us", "Hi again")

        assert store.get_conversation_count("phone1@c.us") == 2
        assert store.get_conversation_count("phone1b@c.us") == 2

    def test_20_patients_3_conversations_each(self):
        """Scale test: 20 patients × 3+ conversations each = 60+ total."""
        store = PatientStore()
        for i in range(20):
            store.add(
                f"phone{i}@c.us",
                f"Patient {i}",
                date(2026, 7, (i % 28) + 1),
            )

        # 3 conversations per patient
        for i in range(20):
            phone = f"phone{i}@c.us"
            store.add_conversation(phone, f"Patient {i}: message 1 — greetings")
            store.add_conversation(phone, f"Patient {i}: message 2 — question about hours")
            store.add_conversation(phone, f"Patient {i}: message 3 — thank you")

        # Verify every patient has 3+ conversations
        for i in range(20):
            count = store.get_conversation_count(f"phone{i}@c.us")
            assert count == 3, f"Patient {i} has {count} conversations, expected 3"
            history = store.get_conversation_history(f"phone{i}@c.us")
            assert len(history) == 3
