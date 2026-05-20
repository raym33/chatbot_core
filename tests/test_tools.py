from pathlib import Path

from app.config import get_settings
from app.domain import DomainProfile
from app.privacy import PrivacyProcessor
from app.tools import ToolRegistry


def test_tool_registry_returns_appointment_slots() -> None:
    settings = get_settings()
    profile = DomainProfile.default("Demo", "company")
    registry = ToolRegistry(settings, profile, PrivacyProcessor(redact_pii=True))

    result = registry.invoke("appointment.availability", {"service": "demo"})

    assert result.ok
    assert result.data["slots"]


def test_tool_registry_prepares_incident_ticket() -> None:
    settings = get_settings()
    profile = DomainProfile.default("Demo", "company")
    registry = ToolRegistry(settings, profile, PrivacyProcessor(redact_pii=True))

    result = registry.invoke("incident.create", {"description": "No funciona el acceso"})

    assert result.ok
    assert result.data["ticket_id"].startswith("TCK-")


def test_hospital_registry_can_create_demo_appointment() -> None:
    settings = get_settings()
    profile = DomainProfile.from_file(Path("skills/hospital/profile.json"))
    registry = ToolRegistry(settings, profile, PrivacyProcessor(redact_pii=True))

    availability = registry.invoke("appointment.availability", {"service": "dermatology"})
    slot_id = availability.data["slots"][0]["slot_id"]
    created = registry.invoke(
        "appointment.create",
        {"service": "dermatology", "slot_id": slot_id, "contact_ref": "demo-patient"},
    )

    assert availability.ok
    assert created.ok
    assert created.data["appointment_id"].startswith("APT-")


def test_hospital_registry_returns_admission_status() -> None:
    settings = get_settings()
    profile = DomainProfile.from_file(Path("skills/hospital/profile.json"))
    registry = ToolRegistry(settings, profile, PrivacyProcessor(redact_pii=True))

    result = registry.invoke("hospital.admission_status", {"area": "general"})

    assert result.ok
    assert "required_documents" in result.data
    assert result.data["required_documents"]


def test_hospital_registry_extracts_redacted_text_from_document() -> None:
    settings = get_settings()
    profile = DomainProfile.from_file(Path("skills/hospital/profile.json"))
    registry = ToolRegistry(settings, profile, PrivacyProcessor(redact_pii=True))

    result = registry.invoke(
        "document_ocr.extract",
        {
            "document_ref": str(
                settings.demo_backend_dir / "hospital" / "documents" / "admission_authorization.txt"
            ),
            "purpose": "admission_review",
        },
    )

    assert result.ok
    assert result.data["text_ref"].endswith(".redacted.txt")
    assert result.data["pii_redacted"] is True
