from __future__ import annotations

import re
from dataclasses import dataclass


PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone", re.compile(r"(?<!\d)(?:\+34\s?)?(?:[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3})(?!\d)")),
    ("dni_nie", re.compile(r"\b(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b", re.IGNORECASE)),
    ("iban", re.compile(r"\bES\d{2}(?:\s?\d{4}){5}\b", re.IGNORECASE)),
    ("credit_card", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("postal_address", re.compile(r"\b(?:calle|c/|avenida|avda\.?|plaza|paseo)\s+[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ .,-]{4,80}", re.IGNORECASE)),
    ("health_record", re.compile(r"\b(?:historia clinica|n[úu]mero de historia|nhc)\s*[:#]?\s*[A-Za-z0-9-]{4,}\b", re.IGNORECASE)),
]


@dataclass(slots=True)
class PrivacyReport:
    redacted_text: str
    detected_types: list[str]
    redaction_count: int


class PrivacyProcessor:
    def __init__(self, redact_pii: bool = True) -> None:
        self.redact_pii = redact_pii

    def process(self, text: str) -> PrivacyReport:
        detected: list[str] = []
        redacted = text
        count = 0

        for pii_type, pattern in PII_PATTERNS:
            matches = list(pattern.finditer(redacted))
            if not matches:
                continue
            detected.append(pii_type)
            if self.redact_pii:
                redacted, replacements = pattern.subn(f"[REDACTED_{pii_type.upper()}]", redacted)
                count += replacements

        return PrivacyReport(
            redacted_text=redacted,
            detected_types=sorted(set(detected)),
            redaction_count=count,
        )
