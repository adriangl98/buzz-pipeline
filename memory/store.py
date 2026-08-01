"""Patient memory store — remembers patients by phone across conversations."""
from datetime import datetime, date, timezone
from typing import Optional


class PatientStore:
    """In-memory store for patient records indexed by WhatsApp phone.

    Supports:
    - Add/update patients
    - Lookup by phone
    - Link alternate phone numbers (identity verification)
    - Find by name (flags same-name-different-phone)
    - Conversation tracking (count + history)
    """

    def __init__(self):
        self._by_phone: dict[str, dict] = {}
        self._aliases: dict[str, str] = {}  # new_phone -> canonical_phone
        self._conversations: dict[str, list[dict]] = {}  # phone -> messages

    def add(self, phone: str, name: str, last_visit: date) -> dict:
        """Add a new patient record."""
        record = {
            "phone": phone,
            "name": name,
            "last_visit": last_visit.isoformat(),
        }
        self._by_phone[phone] = record
        return record

    def get_by_phone(self, phone: str) -> Optional[dict]:
        """Look up a patient by their WhatsApp phone number.

        Follows alias chain for linked phone numbers.
        """
        canonical = self._resolve_phone(phone)
        return self._by_phone.get(canonical)

    def update_last_visit(self, phone: str, last_visit: date) -> Optional[dict]:
        """Update the last_visit date for a returning patient."""
        canonical = self._resolve_phone(phone)
        record = self._by_phone.get(canonical)
        if record is None:
            return None
        record["last_visit"] = last_visit.isoformat()
        return record

    def link_phone(self, existing_phone: str, new_phone: str) -> bool:
        """Link an alternate phone number to an existing patient.

        After linking, both phones resolve to the same patient record.
        """
        canonical = self._resolve_phone(existing_phone)
        if canonical not in self._by_phone:
            return False
        self._aliases[new_phone] = canonical
        return True

    def find_by_name(self, name: str) -> list[dict]:
        """Find patient records matching a name (case-insensitive)."""
        name_lower = name.lower()
        matches = []
        seen = set()
        for record in self._by_phone.values():
            if record["name"].lower() == name_lower:
                if record["phone"] not in seen:
                    matches.append(dict(record))
                    seen.add(record["phone"])
        return matches

    def count(self) -> int:
        """Return the total number of unique patients."""
        return len(self._by_phone)

    # ── conversation tracking (Ticket 2) ─────────────────────────

    def add_conversation(self, phone: str, message: str) -> None:
        """Record a conversation message for a patient.

        Resolves through aliases. Creates the conversation list
        if the patient hasn't had one yet.
        """
        canonical = self._resolve_phone(phone)
        if canonical not in self._conversations:
            self._conversations[canonical] = []
        self._conversations[canonical].append({
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_conversation_count(self, phone: str) -> int:
        """Return the number of recorded conversations for a patient."""
        canonical = self._resolve_phone(phone)
        messages = self._conversations.get(canonical, [])
        return len(messages)

    def get_conversation_history(self, phone: str) -> list[dict]:
        """Return the full conversation history for a patient."""
        canonical = self._resolve_phone(phone)
        return list(self._conversations.get(canonical, []))

    # ── internal ──────────────────────────────────────────────────

    def _resolve_phone(self, phone: str) -> str:
        """Resolve alias chain to canonical phone number."""
        while phone in self._aliases:
            phone = self._aliases[phone]
        return phone
