"""Patient memory store — remembers patients by phone across conversations."""
from datetime import date
from typing import Optional


class PatientStore:
    """In-memory store for patient records indexed by WhatsApp phone.

    Supports:
    - Add/update patients
    - Lookup by phone
    - Link alternate phone numbers (identity verification)
    - Find by name (flags same-name-different-phone)
    """

    def __init__(self):
        self._by_phone: dict[str, dict] = {}
        self._aliases: dict[str, str] = {}  # new_phone -> canonical_phone

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

    def _resolve_phone(self, phone: str) -> str:
        """Resolve alias chain to canonical phone number."""
        while phone in self._aliases:
            phone = self._aliases[phone]
        return phone
