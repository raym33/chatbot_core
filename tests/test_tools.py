from app.config import get_settings
from app.domain import DomainProfile
from app.tools import ToolRegistry


def test_tool_registry_returns_appointment_slots() -> None:
    settings = get_settings()
    profile = DomainProfile.default("Demo", "company")
    registry = ToolRegistry(settings, profile)

    result = registry.invoke("appointment.availability", {"service": "demo"})

    assert result.ok
    assert result.data["slots"]


def test_tool_registry_prepares_incident_ticket() -> None:
    settings = get_settings()
    profile = DomainProfile.default("Demo", "company")
    registry = ToolRegistry(settings, profile)

    result = registry.invoke("incident.create", {"description": "No funciona el acceso"})

    assert result.ok
    assert result.data["ticket_id"].startswith("TCK-")
