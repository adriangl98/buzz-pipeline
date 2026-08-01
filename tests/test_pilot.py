"""Pilot readiness: 20 patients, 60 convos, <5s, 95% accuracy."""
import time
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

# 20 simulated Laredo patients
PATIENTS = [
    ("Maria Garcia",   "521111111111@c.us", "es"),
    ("John Smith",     "12222222222@c.us",   "en"),
    ("Ana Lopez",      "521333333333@c.us", "es"),
    ("Robert Johnson", "14444444444@c.us",   "en"),
    ("Carlos Mendez",  "521555555555@c.us", "es"),
    ("Emily Davis",    "16666666666@c.us",   "en"),
    ("Sofia Ramirez",  "521777777777@c.us", "es"),
    ("Michael Brown",  "18888888888@c.us",   "en"),
    ("Isabella Torres","521999999999@c.us", "es"),
    ("James Wilson",   "11010101010@c.us",   "en"),
    ("Valentina Flores","521121212121@c.us","es"),
    ("David Martinez", "521131313131@c.us",  "es"),
    ("Sarah Anderson", "11414141414@c.us",   "en"),
    ("Daniel Hernandez","521151515151@c.us","es"),
    ("Jessica Taylor", "11616161616@c.us",   "en"),
    ("Luis Gonzalez",  "521171717171@c.us",  "es"),
    ("Amanda Thomas",  "11818181818@c.us",   "en"),
    ("Miguel Ruiz",    "521191919191@c.us",  "es"),
    ("Patricia Moore", "12020202020@c.us",   "en"),
    ("Elena Vasquez",  "521212121212@c.us",  "es"),
]

EN_QS = [
    ("What are your office hours?",         "hour"),
    ("Where are you located?",              "located"),
    ("Do you do braces?",                   "braces"),
]
ES_QS = [
    ("¿Cuál es su horario?",   "horario"),
    ("¿Dónde están ubicados?", "ubicado"),
    ("¿Hacen frenos?",         "frenos"),
]


def _payload(name, phone, question):
    return {
        "event": "message",
        "data": {
            "from": phone,
            "to": "18005551234@c.us",
            "body": question,
            "type": "chat",
            "notifyName": name,
        },
    }


class TestPilotReadiness:
    """Pilot acceptance for hermes-local-mvp."""

    @pytest.mark.asyncio
    async def test_20_patients_60_conversations(self):
        """20 patients × 3 questions = 60 convos, all 200."""
        from gateway.server import create_app
        from faq.knowledge import FAQ

        mock_send = AsyncMock(return_value=True)
        app = create_app(FAQ())
        count = 0

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                for name, phone, lang in PATIENTS:
                    qs = ES_QS if lang == "es" else EN_QS
                    for question, _ in qs:
                        resp = await client.post(
                            "/webhook", json=_payload(name, phone, question)
                        )
                        assert resp.status_code == 200, resp.json()
                        count += 1

        assert count == 60, f"Expected 60, got {count}"

    @pytest.mark.asyncio
    async def test_response_under_5_seconds(self):
        """Every response completes in under 5 seconds."""
        from gateway.server import create_app
        from faq.knowledge import FAQ

        mock_send = AsyncMock(return_value=True)
        app = create_app(FAQ())
        timings = []

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                for name, phone, lang in PATIENTS:
                    qs = ES_QS if lang == "es" else EN_QS
                    for question, _ in qs:
                        start = time.monotonic()
                        await client.post(
                            "/webhook", json=_payload(name, phone, question)
                        )
                        timings.append(time.monotonic() - start)

        slow = [t for t in timings if t >= 5.0]
        assert not slow, f"{len(slow)} responses >= 5s. Max: {max(timings):.3f}s"
        avg = sum(timings) / len(timings)
        assert avg < 1.0, f"Avg {avg:.3f}s exceeds 1s"

    @pytest.mark.asyncio
    async def test_accuracy_above_95_percent(self):
        """FAQ answers contain expected keywords (≥95%)."""
        from gateway.server import create_app
        from faq.knowledge import FAQ

        mock_send = AsyncMock(return_value=True)
        app = create_app(FAQ())
        correct = 0
        total = 0

        with patch("gateway.server.send_message", mock_send):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                for name, phone, lang in PATIENTS:
                    qs = ES_QS if lang == "es" else EN_QS
                    for question, expected in qs:
                        await client.post(
                            "/webhook", json=_payload(name, phone, question)
                        )
                        total += 1
                        sent = mock_send.call_args_list[-1][1]["body"].lower()
                        if expected in sent:
                            correct += 1

        accuracy = (correct / total) * 100
        assert accuracy >= 95.0, f"Accuracy {accuracy:.1f}% < 95% ({correct}/{total})"
