"""Pilot documentation validation tests (Ticket 2 — pilot readiness).

Validates that deployment and training documentation exists and covers
all required sections per acceptance criteria.
"""
import os
import pytest


DOCS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDeploymentDocs:
    """Deployment guide completeness."""

    def test_deploy_md_exists(self):
        """DEPLOY.md must exist in the project root."""
        path = os.path.join(DOCS_DIR, "DEPLOY.md")
        assert os.path.isfile(path), f"DEPLOY.md not found at {path}"

    def test_deploy_md_has_required_sections(self):
        """DEPLOY.md must cover: overview, prerequisites, quick start, services, config, verification."""
        path = os.path.join(DOCS_DIR, "DEPLOY.md")
        with open(path) as f:
            content = f.read().lower()

        required = [
            "overview",
            "prerequisites",
            "quick start",
            "services",
            "configuration",
            "verification",
            "troubleshooting",
        ]
        for section in required:
            assert section in content, f"DEPLOY.md missing section: {section}"

    def test_deploy_md_has_architecture_diagram(self):
        """DEPLOY.md must document the system architecture."""
        path = os.path.join(DOCS_DIR, "DEPLOY.md")
        with open(path) as f:
            content = f.read()

        assert "WhatsApp" in content and "Gateway" in content, \
            "DEPLOY.md missing architecture description"


class TestOwnerTrainingDocs:
    """Owner training guide completeness."""

    def test_owner_guide_md_exists(self):
        """OWNER_GUIDE.md must exist in the project root."""
        path = os.path.join(DOCS_DIR, "OWNER_GUIDE.md")
        assert os.path.isfile(path), f"OWNER_GUIDE.md not found at {path}"

    def test_owner_guide_covers_what_ai_handles(self):
        """Owner guide must explain what the AI handles automatically."""
        path = os.path.join(DOCS_DIR, "OWNER_GUIDE.md")
        with open(path) as f:
            content = f.read().lower()

        assert "hours" in content, "Missing: office hours coverage"
        assert "insurance" in content, "Missing: insurance coverage"
        assert "location" in content or "parking" in content, "Missing: location/parking"

    def test_owner_guide_covers_escalation(self):
        """Owner guide must explain escalation triggers and SMS workflow."""
        path = os.path.join(DOCS_DIR, "OWNER_GUIDE.md")
        with open(path) as f:
            content = f.read().lower()

        assert "escalation" in content, "Missing: escalation explanation"
        assert "sms" in content, "Missing: SMS workflow"

    def test_owner_guide_has_daily_checklist(self):
        """Owner guide must include a daily operational checklist."""
        path = os.path.join(DOCS_DIR, "OWNER_GUIDE.md")
        with open(path) as f:
            content = f.read()

        assert "Daily" in content or "daily" in content or "Checklist" in content or "checklist" in content, \
            "Missing: daily checklist"

    def test_owner_guide_has_pilot_metrics(self):
        """Owner guide must document pilot success metrics."""
        path = os.path.join(DOCS_DIR, "OWNER_GUIDE.md")
        with open(path) as f:
            content = f.read().lower()

        assert "accuracy" in content, "Missing: accuracy metrics"
        assert "response time" in content or "5 second" in content, "Missing: response time target"


class TestPilotMetricValidation:
    """Validate that the system meets pilot metrics."""

    def test_20_patients_supported(self):
        """System supports 20 unique patients."""
        from memory.store import PatientStore
        from datetime import date

        store = PatientStore()
        for i in range(20):
            store.add(f"phone{i}@c.us", f"Patient {i}", date(2026, 7, (i % 28) + 1))

        assert store.count() == 20

    def test_50_plus_conversations_feasible(self):
        """System can handle 50+ conversations across patients."""
        from memory.store import PatientStore
        from datetime import date

        store = PatientStore()
        for i in range(20):
            store.add(f"phone{i}@c.us", f"Patient {i}", date(2026, 7, 1))
            store.add_conversation(f"phone{i}@c.us", f"msg 1 from patient {i}")
            store.add_conversation(f"phone{i}@c.us", f"msg 2 from patient {i}")
            store.add_conversation(f"phone{i}@c.us", f"msg 3 from patient {i}")

        total = sum(store.get_conversation_count(f"phone{i}@c.us") for i in range(20))
        assert total == 60

    def test_faq_response_time_under_5_seconds(self):
        """FAQ lookup completes in under 100ms (well within 5s SLA)."""
        import time
        from faq.knowledge import FAQ

        faq = FAQ()
        questions = [
            "What are your hours?", "¿Dónde están ubicados?",
            "What insurance do you accept?", "¿Qué servicios ofrecen?",
            "I'm a new patient",
        ]

        start = time.perf_counter()
        for q in questions * 20:  # 100 lookups
            faq.ask(q)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000
        assert avg_ms < 100, f"Avg FAQ lookup: {avg_ms:.1f}ms, expected <100ms"
