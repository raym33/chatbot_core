from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Any

from app.config import Settings
from app.connectors import LocalHospitalReferenceConnectors
from app.domain import DomainProfile
from app.models import ToolResult
from app.privacy import PrivacyProcessor


class ToolRegistry:
    def __init__(self, settings: Settings, profile: DomainProfile, privacy: PrivacyProcessor) -> None:
        self.settings = settings
        self.profile = profile
        self.privacy = privacy
        self.hospital_connectors = LocalHospitalReferenceConnectors(settings, privacy)

    def list_tools(self) -> list[dict[str, Any]]:
        tools = [
            {
                "name": "appointment.availability",
                "description": "Devuelve huecos simulados de reserva o cita para el dominio activo.",
                "domains": ["cityhall", "hospital", "company", "general"],
            },
            {
                "name": "appointment.create",
                "description": "Crea una reserva demostrativa sobre el slot elegido.",
                "domains": ["hospital", "company", "general"],
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
        if self.profile.organization_type == "hospital":
            tools.extend(
                [
                    {
                        "name": "hospital.admission_status",
                        "description": "Consulta requisitos y horario de admision.",
                        "domains": ["hospital"],
                    },
                    {
                        "name": "document_ocr.extract",
                        "description": "Extrae y redacta texto de un documento autorizado.",
                        "domains": ["hospital", "dental_clinic", "aesthetic_clinic", "legal_office"],
                    },
                ]
            )
        return tools

    def invoke(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if name == "appointment.availability":
            return self._appointment_availability(arguments)
        if name == "appointment.create":
            return self._appointment_create(arguments)
        if name == "incident.create":
            return self._incident_create(arguments)
        if name == "handoff.create":
            return self._handoff_create(arguments)
        if name == "hospital.admission_status":
            return self._hospital_admission_status(arguments)
        if name == "document_ocr.extract":
            return self._document_ocr_extract(arguments)
        return ToolResult(
            name=name,
            ok=False,
            summary=f"Herramienta no registrada: {name}",
            data={},
        )

    def for_intent(self, intent: str, user_text: str) -> ToolResult | None:
        if intent == "appointment":
            return self._appointment_availability({"query": user_text})
        if intent == "admission" and self.profile.organization_type == "hospital":
            return self._hospital_admission_status({"area": "general"})
        if intent == "incident":
            return self._incident_create({"description": user_text, "dry_run": True})
        if intent == "escalation":
            return self._handoff_create({"reason": user_text, "dry_run": True, "queue": self._handoff_queue()})
        return None

    def _appointment_availability(self, arguments: dict[str, Any]) -> ToolResult:
        service = str(arguments.get("service") or arguments.get("query") or "servicio general")
        if self.profile.organization_type == "hospital":
            payload = self.hospital_connectors.availability(
                service=service,
                location=arguments.get("location"),
                date_from=arguments.get("date_from"),
            )
            return ToolResult(
                name="appointment.availability",
                ok=True,
                summary=(
                    f"He localizado {len(payload['slots'])} huecos orientativos para "
                    f"{payload['specialty']} en {payload['location']}."
                ),
                data={
                    **payload,
                    "booking_url": self.settings.appointment_url,
                },
            )

        return ToolResult(
            name="appointment.availability",
            ok=True,
            summary=f"He preparado 3 huecos orientativos para {service}.",
            data={
                "service": service,
                "slots": self._fallback_slots(),
                "booking_url": self.settings.appointment_url,
            },
        )

    def _appointment_create(self, arguments: dict[str, Any]) -> ToolResult:
        if self.profile.organization_type != "hospital":
            return ToolResult(
                name="appointment.create",
                ok=False,
                summary="La creacion demostrativa de citas solo esta implementada en la vertical hospital.",
                data={},
            )
        try:
            payload = self.hospital_connectors.create_appointment(
                service=str(arguments.get("service") or "general"),
                slot_id=str(arguments.get("slot_id") or ""),
                contact_ref=str(arguments.get("contact_ref") or "demo-contact"),
                notes=arguments.get("notes"),
            )
        except ValueError:
            return ToolResult(
                name="appointment.create",
                ok=False,
                summary="No he encontrado el slot indicado para cerrar la reserva demostrativa.",
                data={},
            )
        return ToolResult(
            name="appointment.create",
            ok=True,
            summary=f"He preparado una reserva demostrativa con referencia {payload['appointment_id']}.",
            data=payload,
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
        if self.profile.organization_type == "hospital":
            payload = self.hospital_connectors.create_handoff(
                queue=str(arguments.get("queue") or self._handoff_queue()),
                reason=reason,
                contact_ref=arguments.get("contact_ref"),
            )
            return ToolResult(
                name="handoff.create",
                ok=True,
                summary=(
                    f"He preparado el escalado humano con ticket {payload['handoff_id']} "
                    f"para la cola {payload['queue']}."
                ),
                data={**payload, "handoff_url": self.settings.human_handoff_url},
            )

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

    def _hospital_admission_status(self, arguments: dict[str, Any]) -> ToolResult:
        if self.profile.organization_type != "hospital":
            return ToolResult(
                name="hospital.admission_status",
                ok=False,
                summary="La consulta de admision solo esta disponible para la vertical hospital.",
                data={},
            )
        payload = self.hospital_connectors.admission_status(
            area=arguments.get("area"),
            patient_type=arguments.get("patient_type"),
        )
        return ToolResult(
            name="hospital.admission_status",
            ok=True,
            summary=(
                f"Admision {payload['area']}: {payload['hours']}. "
                f"Documentos orientativos: {', '.join(payload['required_documents'][:3])}."
            ),
            data=payload,
        )

    def _document_ocr_extract(self, arguments: dict[str, Any]) -> ToolResult:
        if self.profile.organization_type != "hospital":
            return ToolResult(
                name="document_ocr.extract",
                ok=False,
                summary="El OCR demostrativo solo esta implementado en la vertical hospital.",
                data={},
            )
        try:
            payload = self.hospital_connectors.extract_document(
                document_ref=str(arguments.get("document_ref") or ""),
                purpose=str(arguments.get("purpose") or "administrative_review"),
            )
        except ValueError as exc:
            return ToolResult(
                name="document_ocr.extract",
                ok=False,
                summary=self._ocr_error_message(str(exc)),
                data={},
            )
        return ToolResult(
            name="document_ocr.extract",
            ok=True,
            summary="He extraido el texto del documento y he generado una version redactada para revision.",
            data=payload,
        )

    def _appointment_channel(self) -> str:
        if self.profile.organization_type == "hospital":
            return "admision"
        if self.profile.organization_type == "company":
            return "sales_or_support"
        if self.profile.organization_type == "cityhall":
            return "sede_o_010"
        return "support"

    def _handoff_queue(self) -> str:
        if self.profile.organization_type == "hospital":
            return "admission"
        return "support"

    def _ocr_error_message(self, error_code: str) -> str:
        if error_code == "invalid_document_ref":
            return "La referencia documental no esta permitida por la politica del conector OCR."
        if error_code == "document_not_found":
            return "No encuentro el documento indicado para OCR."
        if error_code == "unsupported_document_type":
            return "El conector OCR de referencia admite txt, md y algunas imagenes."
        if error_code == "ocr_engine_unavailable":
            return "No hay motor OCR de sistema disponible para procesar imagenes en este nodo."
        return "No he podido procesar el documento."

    def _fallback_slots(self) -> list[dict[str, Any]]:
        base = date.today() + timedelta(days=1)
        return [
            {
                "date": (base + timedelta(days=offset)).isoformat(),
                "time": time,
                "channel": self._appointment_channel(),
            }
            for offset, time in [(0, "09:30"), (1, "11:00"), (2, "13:15")]
        ]
