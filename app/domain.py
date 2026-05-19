from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DomainProfile:
    name: str
    organization_type: str
    assistant_name: str
    default_locale: str = "es-ES"
    audience: str = "usuarios finales"
    tone: str = "claro, profesional y cercano"
    first_turn_style: str = "trato de usted"
    response_rules: list[str] = field(default_factory=list)
    escalation_rules: list[str] = field(default_factory=list)
    restricted_topics: list[str] = field(default_factory=list)
    supported_intents: list[str] = field(default_factory=list)
    tool_labels: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "DomainProfile":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(**payload)

    @classmethod
    def default(cls, organization_name: str, organization_type: str) -> "DomainProfile":
        labels = {
            "contact": "Hablar con soporte humano",
            "appointment": "Abrir reserva o cita",
            "incident": "Registrar incidencia",
            "faq": "Ver informacion ampliada",
        }
        return cls(
            name=organization_name,
            organization_type=organization_type,
            assistant_name="Chatbot Core",
            audience="ciudadania, pacientes, clientes o personal interno",
            response_rules=[
                "No inventar datos no sustentados por contexto o herramientas.",
                "Citar siempre la fuente cuando la respuesta sea factual.",
                "Priorizar una respuesta breve y una accion siguiente clara.",
            ],
            escalation_rules=[
                "Escalar cuando falte contexto verificable.",
                "Escalar en temas sensibles o de alto riesgo.",
            ],
            restricted_topics=[
                "diagnosticos medicos definitivos",
                "asesoramiento legal vinculante",
                "decisiones administrativas finales",
            ],
            supported_intents=["faq", "appointment", "incident", "escalation"],
            tool_labels=labels,
        )
