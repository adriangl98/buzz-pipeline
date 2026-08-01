"""Unit tests for FAQ knowledge base — Laredo Dental FAQ (Ticket 3).

Tests all FAQ topics (hours, location, insurance, services, new_patient),
keyword matching, bilingual responses, and edge cases.
"""
import pytest
from faq.knowledge import FAQ


class TestFAQAnswers:
    """All 5 FAQ topics return correct bilingual answers."""

    def test_hours_english(self):
        faq = FAQ()
        answer = faq.ask("What are your office hours?")
        assert answer is not None
        assert "Monday through Friday" in answer
        assert "8:00 AM to 5:00 PM" in answer

    def test_hours_spanish(self):
        faq = FAQ()
        answer = faq.ask("¿Cuáles son sus horarios?")
        assert answer is not None
        assert "lunes a viernes" in answer
        assert "8:00 AM" in answer

    def test_location_english(self):
        faq = FAQ()
        answer = faq.ask("Where are you located?")
        assert answer is not None
        assert "San Bernardo" in answer
        assert "Laredo, TX 78040" in answer

    def test_location_includes_parking(self):
        """Parking info is included in location answer."""
        faq = FAQ()
        answer = faq.ask("Is there parking available?")
        assert answer is not None
        assert "parking" in answer.lower()

    def test_location_spanish(self):
        faq = FAQ()
        answer = faq.ask("¿Dónde están ubicados?")
        assert answer is not None
        assert "San Bernardo" in answer
        assert "estacionamiento" in answer

    def test_insurance_english(self):
        faq = FAQ()
        answer = faq.ask("What insurance do you accept?")
        assert answer is not None
        assert "Delta Dental" in answer
        assert "Aetna" in answer
        assert "Cigna" in answer

    def test_insurance_spanish(self):
        faq = FAQ()
        answer = faq.ask("¿Qué seguros aceptan?")
        assert answer is not None
        assert "Delta Dental" in answer

    def test_services_english(self):
        faq = FAQ()
        answer = faq.ask("What services do you offer?")
        assert answer is not None
        assert "cleaning" in answer.lower() or "cleanings" in answer.lower()
        assert "filling" in answer.lower() or "fillings" in answer.lower()

    def test_services_spanish(self):
        faq = FAQ()
        answer = faq.ask("¿Qué servicios ofrecen?")
        assert answer is not None
        assert "limpieza" in answer.lower() or "limpiezas" in answer.lower()
        assert "relleno" in answer.lower() or "rellenos" in answer.lower()

    def test_new_patient_english(self):
        faq = FAQ()
        answer = faq.ask("I'm a new patient, how do I start?")
        assert answer is not None
        assert "new patients" in answer.lower()
        assert "name" in answer.lower()
        assert "phone" in answer.lower()

    def test_new_patient_spanish(self):
        faq = FAQ()
        answer = faq.ask("Soy nuevo paciente, ¿qué necesito?")
        assert answer is not None
        assert "pacientes nuevos" in answer.lower()
        assert "nombre" in answer.lower()
        assert "teléfono" in answer.lower()


class TestKeywordMatching:
    """Keyword matching logic and edge cases."""

    def test_matches_hours_by_keyword_hour(self):
        faq = FAQ()
        answer = faq.ask("What hour do you open?")
        assert answer is not None
        assert "Monday" in answer

    def test_matches_hours_by_keyword_schedule(self):
        faq = FAQ()
        answer = faq.ask("What's your schedule?")
        assert answer is not None
        assert "Monday" in answer

    def test_matches_location_by_keyword_address(self):
        faq = FAQ()
        answer = faq.ask("What's your address?")
        assert answer is not None
        assert "San Bernardo" in answer

    def test_matches_insurance_by_keyword_coverage(self):
        faq = FAQ()
        answer = faq.ask("What coverage do you have?")
        assert answer is not None
        assert "Delta Dental" in answer

    def test_matches_services_by_keyword_cleaning(self):
        faq = FAQ()
        answer = faq.ask("Do you do teeth cleaning?")
        assert answer is not None
        assert "cleaning" in answer.lower()

    def test_no_match_returns_none(self):
        faq = FAQ()
        answer = faq.ask("What's the weather like today?")
        assert answer is None

    def test_no_match_unrelated_question(self):
        faq = FAQ()
        answer = faq.ask("Do you sell toothbrushes?")
        assert answer is None

    def test_matches_best_topic_when_multiple_keywords(self):
        """When question matches multiple topics, highest-scoring wins."""
        faq = FAQ()
        # "insurance" and "location" both match "parking" keyword
        # "parking" is in location keywords
        answer = faq.ask("Where can I park?")
        assert answer is not None
        assert "San Bernardo" in answer  # location wins


class TestClassify:
    """Topic classification returns the matched topic."""

    def test_classify_returns_topic(self):
        faq = FAQ()
        topic = faq._classify("What are your hours?")
        assert topic == "hours"

    def test_classify_returns_none_for_no_match(self):
        faq = FAQ()
        topic = faq._classify("random text")
        assert topic is None

    def test_classify_new_patient(self):
        faq = FAQ()
        topic = faq._classify("I'm a new patient")
        assert topic == "new_patient"


class TestLanguageDetection:
    """FAQ detects Spanish vs English for response language."""

    def test_detects_spanish(self):
        faq = FAQ()
        lang = faq._detect_language("¿A qué hora abren?")
        assert lang == "es"

    def test_detects_english(self):
        faq = FAQ()
        lang = faq._detect_language("What time do you open?")
        assert lang == "en"

    def test_spanish_markers_take_priority(self):
        faq = FAQ()
        lang = faq._detect_language("gracias")
        assert lang == "es"
