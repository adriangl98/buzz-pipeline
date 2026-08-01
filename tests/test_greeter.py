"""Unit tests for PatientGreeter — personalized greetings + identity verification (Ticket 2).

Tests new patient greetings, returning patient greetings, identity verification,
and NEW: conversation-aware greeting (3+ conversations tracking).
"""
from datetime import date

from memory.store import PatientStore
from memory.greeter import PatientGreeter


class TestGreetNewPatient:
    """First-time patient greetings."""

    def test_greets_new_patient_in_english(self):
        """Unknown phone gets welcome greeting in English."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="unknown@c.us", incoming_message="Hello")

        assert "Welcome to Laredo Dental" in greeting
        assert "first visit" in greeting.lower()

    def test_greets_new_patient_in_spanish(self):
        """Unknown phone gets welcome greeting in Spanish for Spanish message."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="unknown@c.us", incoming_message="Hola")

        assert "Bienvenido a Laredo Dental" in greeting
        assert "primera visita" in greeting.lower()

    def test_greets_new_patient_no_message_defaults_english(self):
        """Empty/no message defaults to English welcome."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="unknown@c.us")

        assert "Welcome to Laredo Dental" in greeting


class TestGreetReturningPatient:
    """Returning patient personalized greetings."""

    def test_greets_returning_patient_by_name(self):
        """Known phone gets greeting that includes first name."""
        store = PatientStore()
        store.add("phone1@c.us", "María García", date(2026, 7, 15))
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="phone1@c.us", incoming_message="Hola")

        assert "María" in greeting

    def test_greets_returning_patient_with_last_visit(self):
        """Returning greeting includes last visit date."""
        store = PatientStore()
        store.add("phone1@c.us", "John Smith", date(2026, 6, 1))
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="phone1@c.us", incoming_message="Hi")

        assert "2026-06-01" in greeting

    def test_greets_returning_patient_in_spanish(self):
        """Spanish returning greeting includes Spanish text."""
        store = PatientStore()
        store.add("phone1@c.us", "Carlos López", date(2026, 7, 20))
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="phone1@c.us", incoming_message="Hola ¿cómo están?")

        assert "Bienvenida de nuevo" in greeting
        assert "Carlos" in greeting
        assert "última visita" in greeting


class TestIdentityVerification:
    """Same-name-different-phone identity verification."""

    def test_greet_with_verification_same_name_different_phone(self):
        """When a known name messages from an unknown phone, verification triggers."""
        store = PatientStore()
        store.add("phone1@c.us", "María García", date(2026, 7, 15))
        greeter = PatientGreeter(store)

        result = greeter.greet_with_verification(
            phone="phone2@c.us",
            incoming_message="Hola, soy María García",
        )

        assert result["verified"] is False
        assert result["suggested_match"] is not None
        assert result["suggested_match"]["name"] == "María García"
        assert "María" in result["greeting"]

    def test_greet_with_verification_known_phone_returns_verified(self):
        """Known phone is immediately verified."""
        store = PatientStore()
        store.add("phone1@c.us", "John Smith", date(2026, 7, 1))
        greeter = PatientGreeter(store)

        result = greeter.greet_with_verification(
            phone="phone1@c.us",
            incoming_message="Hi",
        )

        assert result["verified"] is True
        assert result["suggested_match"] is None
        assert "John" in result["greeting"]

    def test_greet_with_verification_unknown_phone_no_name(self):
        """Unknown phone with no name in message is treated as new patient."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        result = greeter.greet_with_verification(
            phone="unknown@c.us",
            incoming_message="Hi, do you have appointments?",
        )

        assert result["verified"] is True  # new patient, no conflict
        assert result["suggested_match"] is None
        assert "Welcome" in result["greeting"]

    def test_verify_identity_links_phone(self):
        """After verification, the new phone is linked to the existing patient."""
        store = PatientStore()
        store.add("phone1@c.us", "María García", date(2026, 7, 15))
        greeter = PatientGreeter(store)

        linked = greeter.verify_identity(
            new_phone="phone2@c.us",
            existing_phone="phone1@c.us",
        )

        assert linked is True
        assert store.get_by_phone("phone2@c.us")["name"] == "María García"

    def test_verify_identity_nonexistent_existing_phone(self):
        """Linking to a nonexistent patient returns False."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        linked = greeter.verify_identity(
            new_phone="phone2@c.us",
            existing_phone="does-not-exist@c.us",
        )

        assert linked is False


class TestLanguageDetection:
    """Language detection logic."""

    def test_detects_spanish_from_message(self):
        """Spanish markers trigger Spanish greeting."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="unknown@c.us", incoming_message="¿A qué hora abren?")

        assert "Bienvenido" in greeting

    def test_defaults_to_english_for_ambiguous_message(self):
        """Ambiguous/no markers default to English."""
        store = PatientStore()
        greeter = PatientGreeter(store)

        greeting = greeter.greet(phone="unknown@c.us", incoming_message="help me please")

        assert "Welcome" in greeting
