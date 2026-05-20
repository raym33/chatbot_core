from __future__ import annotations

import json
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import Settings
from app.privacy import PrivacyProcessor


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "general"


class LocalHospitalReferenceConnectors:
    """Reference local connectors that make one vertical testable end-to-end."""

    def __init__(self, settings: Settings, privacy: PrivacyProcessor) -> None:
        self.settings = settings
        self.privacy = privacy
        self.base_dir = settings.demo_backend_dir / "hospital"
        self.runtime_dir = self.base_dir / "runtime"
        self.documents_dir = self.base_dir / "documents"
        self.catalog_path = self.base_dir / "appointment_slots.json"
        self.admission_path = self.base_dir / "admission.json"
        self.tickets_path = self.runtime_dir / "tickets.jsonl"
        self.bookings_path = self.runtime_dir / "appointments.jsonl"
        self._ensure_seed_data()

    def availability(
        self,
        service: str,
        location: str | None = None,
        date_from: str | None = None,
    ) -> dict[str, Any]:
        service_slug = _slug(service)
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        services = catalog.get("services", [])
        matches = [
            item
            for item in services
            if service_slug in item["slug"] or item["slug"] in service_slug or service_slug == "general"
        ]
        if not matches:
            matches = services[:1]

        selected = matches[0]
        slots = [self._normalized_slot(slot) for slot in selected.get("slots", [])]
        if location:
            slots = [slot for slot in slots if location.lower() in slot["location"].lower()]
        if date_from:
            slots = [slot for slot in slots if slot["date"] >= date_from]

        return {
            "service": selected["service"],
            "specialty": selected["specialty"],
            "location": selected["default_location"],
            "slots": slots[:3],
            "source": "local_hospital_reference_connector",
        }

    def create_appointment(
        self,
        service: str,
        slot_id: str,
        contact_ref: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        availability = self.availability(service)
        slot = next((item for item in availability["slots"] if item["slot_id"] == slot_id), None)
        if not slot:
            raise ValueError("slot_not_found")

        appointment_id = f"APT-{uuid4().hex[:8].upper()}"
        payload = {
            "appointment_id": appointment_id,
            "service": availability["service"],
            "slot_id": slot_id,
            "contact_ref": contact_ref,
            "notes": self.privacy.process(notes or "").redacted_text if notes else None,
            "status": "reserved_demo",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "slot": slot,
        }
        with self.bookings_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return payload

    def admission_status(self, area: str | None = None, patient_type: str | None = None) -> dict[str, Any]:
        payload = json.loads(self.admission_path.read_text(encoding="utf-8"))
        sections = payload.get("areas", {})
        key = _slug(area or "general").replace("-", "_")
        section = sections.get(key) or sections.get("general", {})
        return {
            "area": section.get("name", "General admission"),
            "patient_type": patient_type or "general",
            "desk": section.get("desk"),
            "hours": section.get("hours"),
            "required_documents": section.get("required_documents", []),
            "notes": section.get("notes", []),
            "source": "local_hospital_reference_connector",
        }

    def create_handoff(
        self,
        queue: str,
        reason: str,
        contact_ref: str | None = None,
    ) -> dict[str, Any]:
        handoff_id = f"HND-{uuid4().hex[:8].upper()}"
        payload = {
            "handoff_id": handoff_id,
            "queue": queue,
            "reason": self.privacy.process(reason).redacted_text,
            "contact_ref": self.privacy.process(contact_ref or "").redacted_text if contact_ref else None,
            "status": "queued_demo",
            "eta_minutes": 20 if queue == "admission" else 35,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.tickets_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return payload

    def extract_document(self, document_ref: str, purpose: str) -> dict[str, Any]:
        path = self._resolve_document_ref(document_ref)
        suffix = path.suffix.lower()
        engine = "plaintext"
        if suffix in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            if not shutil_which("tesseract"):
                raise ValueError("ocr_engine_unavailable")
            engine = "tesseract"
            completed = subprocess.run(
                ["tesseract", str(path), "stdout", "--psm", "6"],
                check=True,
                capture_output=True,
                text=True,
            )
            text = completed.stdout
        else:
            raise ValueError("unsupported_document_type")

        report = self.privacy.process(text)
        text_ref = self.settings.ocr_output_dir / f"{path.stem}.redacted.txt"
        text_ref.parent.mkdir(parents=True, exist_ok=True)
        text_ref.write_text(report.redacted_text, encoding="utf-8")
        return {
            "text_ref": str(text_ref.relative_to(self.settings.demo_backend_dir.parent.parent)),
            "metadata": {
                "filename": path.name,
                "purpose": purpose,
                "engine": engine,
                "size_bytes": path.stat().st_size,
            },
            "pii_redacted": report.redaction_count > 0,
            "preview": report.redacted_text[:280],
        }

    def _resolve_document_ref(self, document_ref: str) -> Path:
        raw = Path(document_ref)
        if raw.is_absolute():
            candidate = raw.resolve()
        else:
            candidate = (self.settings.document_intake_dir / raw).resolve()

        allowed_roots = [
            self.settings.document_intake_dir.resolve(),
            self.documents_dir.resolve(),
        ]
        if not any(str(candidate).startswith(str(root)) for root in allowed_roots):
            raise ValueError("invalid_document_ref")
        if not candidate.exists():
            raise ValueError("document_not_found")
        return candidate

    def _normalized_slot(self, slot: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(slot)
        try:
            slot_date = date.fromisoformat(normalized["date"])
        except (KeyError, ValueError):
            return normalized
        if slot_date < date.today():
            delta_days = (date.today() - slot_date).days + 1
            normalized["date"] = (slot_date + timedelta(days=delta_days)).isoformat()
        return normalized

    def _ensure_seed_data(self) -> None:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        if not self.catalog_path.exists():
            base = date.today() + timedelta(days=1)
            payload = {
                "services": [
                    {
                        "service": "Dermatology follow-up",
                        "slug": "dermatology",
                        "specialty": "Dermatology",
                        "default_location": "Outpatient building, desk 2",
                        "slots": [
                            {
                                "slot_id": "DERM-1",
                                "date": (base + timedelta(days=0)).isoformat(),
                                "time": "09:30",
                                "location": "Outpatient building, desk 2",
                            },
                            {
                                "slot_id": "DERM-2",
                                "date": (base + timedelta(days=2)).isoformat(),
                                "time": "11:15",
                                "location": "Outpatient building, desk 2",
                            },
                            {
                                "slot_id": "DERM-3",
                                "date": (base + timedelta(days=4)).isoformat(),
                                "time": "13:00",
                                "location": "Outpatient building, desk 2",
                            },
                        ],
                    },
                    {
                        "service": "Cardiology consultation",
                        "slug": "cardiology",
                        "specialty": "Cardiology",
                        "default_location": "Specialty clinics, floor 1",
                        "slots": [
                            {
                                "slot_id": "CARD-1",
                                "date": (base + timedelta(days=1)).isoformat(),
                                "time": "10:00",
                                "location": "Specialty clinics, floor 1",
                            },
                            {
                                "slot_id": "CARD-2",
                                "date": (base + timedelta(days=3)).isoformat(),
                                "time": "12:20",
                                "location": "Specialty clinics, floor 1",
                            },
                        ],
                    },
                ]
            }
            self.catalog_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        if not self.admission_path.exists():
            payload = {
                "areas": {
                    "general": {
                        "name": "General admission",
                        "desk": "Main lobby, desk A",
                        "hours": "Monday to Friday, 08:00 to 20:00",
                        "required_documents": [
                            "National ID or passport",
                            "Referral or appointment confirmation",
                            "Insurance or public coverage card if applicable",
                        ],
                        "notes": [
                            "Bring previous authorization if the procedure requires it.",
                            "Use authenticated channels for any clinical record request.",
                        ],
                    }
                }
            }
            self.admission_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        sample_document = self.documents_dir / "admission_authorization.txt"
        if not sample_document.exists():
            sample_document.write_text(
                (
                    "Admission authorization form\n"
                    "Patient: Maria Example\n"
                    "Document ID: 12345678A\n"
                    "Service: Dermatology follow-up\n"
                    "Requested date: 2026-06-08\n"
                ),
                encoding="utf-8",
            )


def shutil_which(binary: str) -> str | None:
    return subprocess.run(
        ["which", binary],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip() or None
