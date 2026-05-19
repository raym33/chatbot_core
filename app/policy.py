from __future__ import annotations

from app.config import Settings
from app.domain import DomainProfile
from app.models import Citation


def build_system_prompt(settings: Settings, profile: DomainProfile, easy_read: bool) -> str:
    style = (
        "Use lectura facil, frases cortas y vocabulario sencillo."
        if easy_read
        else f"Use un tono {profile.tone} y {profile.first_turn_style}."
    )
    rules = "\n".join(f"- {rule}" for rule in profile.response_rules)
    restrictions = "\n".join(f"- {item}" for item in profile.restricted_topics)
    escalation = "\n".join(f"- {rule}" for rule in profile.escalation_rules)

    return (
        f"Eres {profile.assistant_name}, asistente de {profile.name}, una organizacion del tipo "
        f"{profile.organization_type}. Atiendes a {profile.audience}. "
        f"{style} Nunca inventes hechos. Si falta soporte documental o de herramientas, "
        "di claramente que no puedes confirmarlo.\n"
        "Reglas de respuesta:\n"
        f"{rules}\n"
        "Temas restringidos o sensibles:\n"
        f"{restrictions}\n"
        "Cuando debas abstenerte o escalar:\n"
        f"{escalation}\n"
        "Si la respuesta es factual, apoyate solo en el contexto recuperado."
    )


def must_abstain(intent: str, citations: list[Citation], high_risk_terms: list[str], user_text: str) -> bool:
    text = user_text.lower()
    if any(term in text for term in high_risk_terms):
        return True
    if intent == "faq" and not citations:
        return True
    return False


def abstention_message(profile: DomainProfile) -> str:
    if profile.organization_type == "hospital":
        return (
            "No puedo valorar sintomas, interpretar pruebas ni indicar tratamientos o medicacion. "
            "Si hay dolor intenso, dificultad respiratoria, dolor en el pecho, perdida de conciencia "
            "u otro signo urgente, contacte con emergencias o acuda a urgencias. Para dudas no urgentes, "
            "puedo derivarle a admision o al profesional sanitario responsable."
        )
    return (
        f"No puedo confirmar esa informacion con seguridad a partir de las fuentes disponibles de {profile.name}. "
        "Prefiero no inventar una respuesta. Si quiere, puedo redirigirle a soporte humano o reformular la consulta."
    )
