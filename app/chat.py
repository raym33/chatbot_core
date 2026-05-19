from __future__ import annotations

import re
from datetime import datetime, timezone

from app.config import Settings
from app.db import Database
from app.llm import ChatClient, EmbeddingClient, LLMResult
from app.models import ChatContext, ChatResponse, Citation, SuggestedAction
from app.rag import Retriever


APPOINTMENT_HINTS = ("cita", "cita previa", "reservar", "anular", "cancelar")
INCIDENT_HINTS = ("incidencia", "farola", "bache", "basura", "semaforo", "ruido")
ESCALATION_HINTS = ("agente", "persona", "humano", "operador")


class ChatService:
    def __init__(
        self,
        settings: Settings,
        db: Database,
        retriever: Retriever,
        llm: ChatClient,
        embedder: EmbeddingClient | None,
    ) -> None:
        self.settings = settings
        self.db = db
        self.retriever = retriever
        self.llm = llm
        self.embedder = embedder

    async def reply(
        self,
        session_id: str,
        user_text: str,
        channel: str,
        context: ChatContext,
    ) -> ChatResponse:
        user_text = user_text.strip()
        citations = await self._citations(user_text)
        actions = self._actions(user_text)
        response_text = ""
        used_host = None
        confidence = 0.45
        provider = self.llm.provider_name
        model = self.llm.model_name

        intent = self._detect_intent(user_text)
        if intent == "escalation":
            response_text = (
                "Puedo derivarle a una persona del servicio municipal. "
                "Si quiere, pulse el boton de contacto humano y adjuntare el contexto de esta conversacion."
            )
            actions.insert(
                0,
                SuggestedAction(
                    type="escalate",
                    label="Contactar con una persona",
                    target=f"/v1/sessions/{session_id}/escalate",
                ),
            )
            confidence = 0.93
        elif intent == "appointment":
            response_text = self._appointment_response(citations)
            confidence = 0.84
        elif intent == "incident":
            response_text = self._incident_response(citations)
            confidence = 0.82
        else:
            llm_result = await self._generate_with_llm(user_text, citations, context)
            used_host = llm_result.host
            provider = llm_result.provider
            model = llm_result.model
            if llm_result.text:
                response_text = llm_result.text
                confidence = min(0.98, 0.62 + min(len(citations), 4) * 0.08)
            else:
                response_text = self._fallback_response(citations, context.easy_read)
                confidence = 0.58 if citations else 0.28

        self.db.add_message(
            session_id,
            "user",
            user_text,
            metadata={"channel": channel, "context": context.model_dump()},
        )
        self.db.add_message(
            session_id,
            "assistant",
            response_text,
            metadata={
                "citations": [item.model_dump() for item in citations],
                "actions": [item.model_dump() for item in actions],
                "used_host": used_host,
                "provider": provider,
                "model": model,
            },
        )

        return ChatResponse(
            session_id=session_id,
            content=response_text,
            citations=citations,
            actions=actions,
            confidence=confidence,
            created_at=datetime.now(timezone.utc),
            used_host=used_host,
            provider=provider,
            model=model,
        )

    async def _generate_with_llm(
        self,
        user_text: str,
        citations: list[Citation],
        context: ChatContext,
    ) -> LLMResult:
        if not citations:
            return LLMResult(text="", host=None)

        context_lines = []
        for citation in citations:
            context_lines.append(
                f"- Fuente: {citation.source}\n  Ruta: {citation.path}\n  Texto: {citation.snippet}"
            )

        reading_style = (
            "Usa lectura facil, frases cortas y maximo tres frases."
            if context.easy_read
            else "Responde de forma breve, institucional y clara."
        )
        page_context = f"Pagina actual: {context.page_url}" if context.page_url else "Pagina actual: no disponible"

        messages = [
            {
                "role": "system",
                "content": (
                    f"Eres el asistente automatico del {self.settings.city_name}. "
                    "Nunca inventes hechos. Si la respuesta no esta sustentada por el contexto, dilo claramente. "
                    f"{reading_style} No uses emojis. Tutelas administrativas: no tomas decisiones. "
                    "Cuando uses informacion factual, apoyate solo en el contexto suministrado."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{page_context}\n"
                    "Contexto oficial recuperado:\n"
                    + "\n".join(context_lines)
                    + f"\n\nPregunta ciudadana: {user_text}\n"
                    "Devuelve una respuesta breve en castellano claro, con tono institucional. "
                    "Si falta certeza, dilo sin inventar. Cierra ofreciendo el siguiente paso mas util."
                ),
            },
        ]
        return await self.llm.chat(messages)

    def _fallback_response(self, citations: list[Citation], easy_read: bool) -> str:
        if not citations:
            return (
                "No tengo informacion suficiente y verificada para responder con seguridad. "
                "Puedo intentar otra busqueda si reformula la consulta o derivarle a atencion ciudadana."
            )

        lead = citations[0].snippet
        lead = re.sub(r"\s+", " ", lead).strip()
        sentences = re.split(r"(?<=[.!?])\s+", lead)
        if easy_read:
            summary = " ".join(sentences[: self.settings.easy_read_max_sentences])
        else:
            summary = " ".join(sentences[:2])

        return (
            f"Segun la documentacion municipal disponible, {summary} "
            "Si quiere, puedo resumirselo mejor o indicarle el tramite relacionado."
        )

    async def _citations(self, user_text: str) -> list[Citation]:
        embedder = self.embedder if self.settings.enable_semantic_rag else None
        chunks = await self.retriever.search(
            user_text,
            top_k=self.settings.top_k,
            embedder=embedder,
            lexical_weight=self.settings.lexical_weight,
            semantic_weight=self.settings.semantic_weight,
        )
        return [
            Citation(
                source=chunk.source,
                path=chunk.path,
                snippet=self._clean_snippet(chunk.text),
            )
            for chunk in chunks
        ]

    def _actions(self, user_text: str) -> list[SuggestedAction]:
        text = user_text.lower()
        actions: list[SuggestedAction] = []
        if any(hint in text for hint in APPOINTMENT_HINTS):
            actions.append(
                SuggestedAction(
                    type="link",
                    label="Abrir cita previa",
                    target=self.settings.appointment_url,
                )
            )
        if any(hint in text for hint in INCIDENT_HINTS):
            actions.append(
                SuggestedAction(
                    type="link",
                    label="Reportar incidencia",
                    target=self.settings.incidents_url,
                )
            )
        if not actions:
            actions.append(
                SuggestedAction(
                    type="link",
                    label="Hablar con atencion ciudadana",
                    target=self.settings.human_handoff_url,
                )
            )
        if not any(action.type == "intent" for action in actions):
            actions.append(
                SuggestedAction(
                    type="intent",
                    label="Pedir resumen mas simple",
                    target="easy_read",
                )
            )
        return actions

    def _detect_intent(self, user_text: str) -> str:
        text = user_text.lower()
        if any(hint in text for hint in ESCALATION_HINTS):
            return "escalation"
        if any(hint in text for hint in APPOINTMENT_HINTS):
            return "appointment"
        if any(hint in text for hint in INCIDENT_HINTS):
            return "incident"
        return "faq"

    def _appointment_response(self, citations: list[Citation]) -> str:
        details = ""
        if citations:
            details = f" He localizado informacion relacionada en la fuente \"{citations[0].source}\"."
        return (
            "Puedo orientarle con la cita previa y llevarle al sistema de reserva municipal."
            f"{details} Si me indica el servicio exacto, tambien puedo ayudarle a afinar el tramite antes de abrir la reserva."
        )

    def _incident_response(self, citations: list[Citation]) -> str:
        details = ""
        if citations:
            details = f" Tambien he encontrado referencia util en \"{citations[0].source}\"."
        return (
            "Para registrar una incidencia urbana necesito al menos tipo de problema y ubicacion."
            f"{details} Puede continuar por aqui o abrir directamente el formulario de incidencias."
        )

    def _clean_snippet(self, text: str) -> str:
        cleaned = re.sub(r"`+", "", text)
        cleaned = cleaned.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:420]
