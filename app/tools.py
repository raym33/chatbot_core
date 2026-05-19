from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Any

from app.config import Settings
from app.domain import DomainProfile
from app.models import ToolResult


class ToolRegistry:
    def __init__(self, settings: Settings, profile: DomainProfile) -> None:
        self.settings = settings
        self.profile = profile

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "appointment.availability",
                "description": "Devuelve huecos simulados de reserva o cita para el dominio activo.",
                "domains": ["cityhall", "hospital", "company", "general"],
            },
            {
                "name": "incident.create",
                "description": "Prepara un ticket de incidencia con identificador trazable.",
                "domains": ["cityhall", "hospital", "company", "general"],
            },
            {
                "name": "handoff.create",
                "description": "Prepara una derivacion a soporte humano con contexto.",
                "domains": ["cityhall", "hospital", "company", "general"],
            },
        ]

    def invoke(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if name == "appointment.availability":
            return self._appointment_availability(arguments)
        if name == "incident.create":
            return self._incident_create(arguments)
        if name == "handoff.create":
            return self._handoff_create(arguments)
        return ToolResult(
            name=name,
            ok=False,
            summary=f"Herramienta no registrada: {name}",
            data={},
        )

    def for_intent(self, intent: str, user_text: str) -> ToolResult | None:
        if intent == "appointment":
            return self._appointment_availability({"query": user_text})
        if intent == "incident":
            return self._incident_create({"description": user_text, "dry_run": True})
        if intent == "escalation":
            return self._handoff_create({"reason": user_text, "dry_run": True})
        return None

    def _appointment_availability(self, arguments: dict[str, Any]) -> ToolResult:
        service = str(arguments.get("service") or arguments.get("query") or "servicio general")
        base = date.today() + timedelta(days=1)
        slots = [
            {
                "date": (base + timedelta(days=offset)).isoformat(),
                "time": time,
                "channel": self._appointment_channel(),
            }
            for offset, time in [(0, "09:30"), (1, "11:00"), (2, "13:15")]
        ]
        return ToolResult(
            name="appointment.availability",
            ok=True,
            summary=f"He preparado 3 huecos orientativos para {service}.",
            data={"service": service, "slots": slots, "booking_url": self.settings.appointment_url},
        )

    def _incident_create(self, arguments: dict[str, Any]) -> ToolResult:
        description = str(arguments.get("description") or "incidencia sin descripcion")
        dry_run = bool(arguments.get("dry_run", False))
        ticket = "DRY" if dry_run else "TCK"
        digest = hashlib.sha1(description.encode("utf-8")).hexdigest()[:8].upper()
        label = self.profile.tool_labels.get("incident", "incidencia")
        return ToolResult(
            name="incident.create",
            ok=True,
            summary=f"He preparado el registro de {label.lower()} con referencia {ticket}-{digest}.",
            data={
                "ticket_id": f"{ticket}-{digest}",
                "requires_confirmation": dry_run,
                "incidents_url": self.settings.incidents_url,
            },
        )

    def _handoff_create(self, arguments: dict[str, Any]) -> ToolResult:
        reason = str(arguments.get("reason") or "solicitud de soporte humano")
        digest = hashlib.sha1(reason.encode("utf-8")).hexdigest()[:8].upper()
        return ToolResult(
            name="handoff.create",
            ok=True,
            summary=f"He preparado una derivacion a soporte humano con referencia HND-{digest}.",
            data={
                "handoff_id": f"HND-{digest}",
                "handoff_url": self.settings.human_handoff_url,
            },
        )

    def _appointment_channel(self) -> str:
        if self.profile.organization_type == "hospital":
            return "admision"
        if self.profile.organization_type == "company":
            return "sales_or_support"
        if self.profile.organization_type == "cityhall":
            return "sede_o_010"
        return "support"
