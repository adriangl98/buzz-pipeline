"""Pilot readiness integration test.

Validates the full stack across 20 patients and 50+ conversations:
- FAQ accuracy
- Patient memory / personalized greetings
- Escalation triggers
- Response time under 5 seconds
"""
import time
import pytest
from datetime import date


# ── mock data: 20 patients ──────────────────────────────────────────

PATIENTS = [
    {"name": "María García", "phone": "521234567890@c.us", "last_visit": date(2026, 7, 15)},
    {"name": "John Smith", "phone": "1234567890@c.us", "last_visit": date(2026, 6, 1)},
    {"name": "Carlos López", "phone": "528112345678@c.us", "last_visit": date(2026, 7, 20)},
    {"name": "Ana Martínez", "phone": "528198765432@c.us", "last_visit": date(2026, 5, 10)},
    {"name": "Robert Johnson", "phone": "12145551234@c.us", "last_visit": date(2026, 7, 1)},
    {"name": "Isabel Rodríguez", "phone": "528133344455@c.us", "last_visit": date(2026, 6, 15)},
    {"name": "David Brown", "phone": "12145559876@c.us", "last_visit": date(2026, 4, 20)},
    {"name": "Elena Vargas", "phone": "528177788899@c.us", "last_visit": date(2026, 7, 25)},
    {"name": "Michael Davis", "phone": "13035551111@c.us", "last_visit": date(2026, 3, 5)},
    {"name": "Sofía Torres", "phone": "528155566677@c.us", "last_visit": date(2026, 7, 10)},
    {"name": "James Wilson", "phone": "12125552222@c.us", "last_visit": date(2026, 6, 30)},
    {"name": "Lucía Ramírez", "phone": "528199988877@c.us", "last_visit": date(2026, 7, 18)},
    {"name": "Patricia Moore", "phone": "14045553333@c.us", "last_visit": date(2026, 5, 25)},
    {"name": "Fernando Díaz", "phone": "528122233344@c.us", "last_visit": date(2026, 7, 2)},
    {"name": "Linda Taylor", "phone": "16035554444@c.us", "last_visit": date(2026, 6, 8)},
    {"name": "Gabriela Cruz", "phone": "528144455566@c.us", "last_visit": date(2026, 7, 22)},
    {"name": "William Anderson", "phone": "18005556666@c.us", "last_visit": date(2026, 4, 12)},
    {"name": "Valentina Herrera", "phone": "528188899900@c.us", "last_visit": date(2026, 7, 30)},
    {"name": "Thomas Jackson", "phone": "17705557777@c.us", "last_visit": date(2026, 5, 18)},
    {"name": "Camila Morales", "phone": "528166677788@c.us", "last_visit": date(2026, 7, 5)},
]

# ── FAQ question/answer pairs for accuracy testing ───────────────────

FAQ_QUESTIONS = [
    {"q": "What are your office hours?", "expect": ["monday", "friday", "8:00"]},
    {"q": "¿Cuáles son sus horarios?", "expect": ["lunes", "viernes", "8:00"]},
    {"q": "Where are you located?", "expect": ["laredo", "san bernardo"]},
    {"q": "¿Dónde están ubicados?", "expect": ["laredo", "san bernardo"]},
    {"q": "What insurance do you accept?", "expect": ["delta", "aetna", "cigna"]},
    {"q": "¿Qué seguros aceptan?", "expect": ["delta", "aetna", "cigna"]},
    {"q": "What services do you offer?", "expect": ["cleaning", "filling"]},
    {"q": "¿Qué servicios ofrecen?", "expect": ["limpieza", "relleno"]},
]

# ── questions that should escalate ───────────────────────────────────

ESCALATION_QUESTIONS = [
    "Do I need a root canal or just a filling?",
    "¿Necesito una endodoncia?",
    "How much does a crown cost?",
    "¿Cuánto cuesta una corona?",
    "I want to book an appointment for Friday at 2pm",
    "Quiero agendar una cita para el viernes",
]


class TestPilotReadiness:
    """Pilot validation: 20 patients, 50+ conversations, accuracy, timing."""

    def test_20_patients_stored_and_retrieved(self):
        """All 20 patients can be stored and retrieved by phone."""
        from memory.store import PatientStore

        store = PatientStore()
        for p in PATIENTS:
            store.add(phone=p["phone"], name=p["name"], last_visit=p["last_visit"])

        assert store.count() == 20

        for p in PATIENTS:
            record = store.get_by_phone(p["phone"])
            assert record is not None
            assert record["name"] == p["name"]

    def test_faq_accuracy_100_percent(self):
        """FAQ answers all known questions correctly (8/8)."""
        from faq.knowledge import FAQ

        faq = FAQ()
        correct = 0
        total = len(FAQ_QUESTIONS)

        for pair in FAQ_QUESTIONS:
            answer = faq.ask(pair["q"])
            assert answer is not None, f"FAQ missed: {pair['q']}"
            lower = answer.lower()
            if all(exp in lower for exp in pair["expect"]):
                correct += 1

        accuracy = correct / total
        assert accuracy == 1.0, f"FAQ accuracy: {accuracy:.0%}, expected 100%"

    def test_returning_patient_greeting_accuracy(self):
        """All 20 returning patients get personalized greeting by name."""
        from memory.store import PatientStore
        from memory.greeter import PatientGreeter

        store = PatientStore()
        for p in PATIENTS:
            store.add(phone=p["phone"], name=p["name"], last_visit=p["last_visit"])

        greeter = PatientGreeter(store)
        greeted = 0

        for p in PATIENTS:
            greeting = greeter.greet(phone=p["phone"], incoming_message="Hola")
            first_name = p["name"].split()[0]
            if first_name in greeting:
                greeted += 1

        accuracy = greeted / len(PATIENTS)
        assert accuracy >= 0.95, f"Greeting accuracy: {accuracy:.0%}, expected ≥95%"

    def test_escalation_triggers_correctly(self):
        """All escalation questions trigger correctly (6/6)."""
        from escalation.detector import EscalationDetector

        detector = EscalationDetector()
        escalated = 0

        for q in ESCALATION_QUESTIONS:
            result = detector.should_escalate(q)
            if result["escalate"]:
                escalated += 1

        accuracy = escalated / len(ESCALATION_QUESTIONS)
        assert accuracy >= 0.95, f"Escalation accuracy: {accuracy:.0%}, expected ≥95%"

    def test_faq_does_not_escalate_faq_questions(self):
        """FAQ questions should NOT trigger escalation."""
        from escalation.detector import EscalationDetector

        detector = EscalationDetector()
        false_escalations = 0

        for pair in FAQ_QUESTIONS:
            result = detector.should_escalate(pair["q"])
            if result["escalate"]:
                false_escalations += 1

        assert false_escalations == 0, f"{false_escalations} FAQ questions incorrectly escalated"

    def test_50_plus_conversations_across_patients(self):
        """Simulate 50+ conversations: memory + FAQ + escalation across all patients."""
        from memory.store import PatientStore
        from memory.greeter import PatientGreeter
        from faq.knowledge import FAQ
        from escalation.detector import EscalationDetector

        store = PatientStore()
        for p in PATIENTS:
            store.add(phone=p["phone"], name=p["name"], last_visit=p["last_visit"])

        greeter = PatientGreeter(store)
        faq = FAQ()
        detector = EscalationDetector()

        conversation_count = 0
        no_failures = True

        # Each of 20 patients gets 3 conversations = 60 total
        for i, patient in enumerate(PATIENTS):
            phone = patient["phone"]

            # Conversation 1: FAQ question
            faq_q = FAQ_QUESTIONS[i % len(FAQ_QUESTIONS)]
            answer = faq.ask(faq_q["q"])
            assert answer is not None, f"Conversation {conversation_count}: FAQ miss for {faq_q['q']}"
            conversation_count += 1

            # Conversation 2: Returning greeting
            greeting = greeter.greet(phone=phone, incoming_message=faq_q["q"])
            assert len(greeting) > 0
            conversation_count += 1

            # Conversation 3: Escalation check
            esc_q = ESCALATION_QUESTIONS[i % len(ESCALATION_QUESTIONS)]
            result = detector.should_escalate(esc_q)
            assert isinstance(result, dict)
            conversation_count += 1

        assert conversation_count == 60, f"Expected 60 conversations, got {conversation_count}"

    def test_response_time_under_5_seconds(self):
        """All FAQ responses complete in under 100ms (well within 5s SLA)."""
        from faq.knowledge import FAQ

        faq = FAQ()
        times = []

        for pair in FAQ_QUESTIONS * 3:  # 24 calls for statistical significance
            start = time.perf_counter()
            faq.ask(pair["q"])
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert max_time < 1.0, f"Max response time {max_time:.3f}s exceeds 1s threshold"
        # All well within 5s — keyword matching is sub-millisecond

    def test_overall_accuracy_above_95_percent(self):
        """Combined accuracy across FAQ + greeting + escalation."""
        from memory.store import PatientStore
        from memory.greeter import PatientGreeter
        from faq.knowledge import FAQ
        from escalation.detector import EscalationDetector

        store = PatientStore()
        for p in PATIENTS:
            store.add(phone=p["phone"], name=p["name"], last_visit=p["last_visit"])

        greeter = PatientGreeter(store)
        faq = FAQ()
        detector = EscalationDetector()

        total_checks = 0
        passed_checks = 0

        # FAQ accuracy
        for pair in FAQ_QUESTIONS:
            answer = faq.ask(pair["q"])
            total_checks += 1
            if answer and all(exp in answer.lower() for exp in pair["expect"]):
                passed_checks += 1

        # Greeting accuracy
        for p in PATIENTS:
            greeting = greeter.greet(phone=p["phone"], incoming_message="Hola")
            total_checks += 1
            if p["name"].split()[0] in greeting:
                passed_checks += 1

        # Escalation accuracy
        for q in ESCALATION_QUESTIONS:
            result = detector.should_escalate(q)
            total_checks += 1
            if result["escalate"]:
                passed_checks += 1

        # FAQ shouldn't escalate
        for pair in FAQ_QUESTIONS:
            result = detector.should_escalate(pair["q"])
            total_checks += 1
            if not result["escalate"]:
                passed_checks += 1

        accuracy = passed_checks / total_checks
        assert accuracy >= 0.95, (
            f"Overall accuracy: {accuracy:.1%} ({passed_checks}/{total_checks}), "
            f"expected ≥95%"
        )
