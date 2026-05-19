from __future__ import annotations

import re
from datetime import datetime, timezone

from app.config import Settings
from app.db import Database
from app.domain import DomainProfile
from app.llm import ChatClient, EmbeddingClient, LLMResult
from app.models import ChatContext, ChatResponse, Citation, SuggestedAction
from app.policy import abstention_message, build_system_prompt, must_abstain
from app.privacy import PrivacyProcessor
from app.rag import Retriever
from app.security import InputGuard, security_refusal
from app.tools import ToolRegistry
from app.verifier import GroundingVerifier


APPOINTMENT_HINTS = ("cita", "cita previa", "reservar", "anular", "cancelar")
INCIDENT_HINTS = ("incidencia", "farola", "bache", "basura", "semaforo", "ruido")
ESCALATION_HINTS = ("agente", "persona", "humano", "operador")
COURTESY_MESSAGES = {"ok", "okay", "vale", "gracias", "hola", "buenas", "perfecto", "de acuerdo"}


class ChatService:
    def __init__(
        self,
        settings: Settings,
        db: Database,
        retriever: Retriever,
        llm: ChatClient,
        embedder: EmbeddingClient | None,
        profile: DomainProfile,
        tools: ToolRegistry,
        verifier: GroundingVerifier,
        input_guard: InputGuard,
        privacy: PrivacyProcessor,
    ) -> None:
        self.settings = settings
        self.db = db
        self.retriever = retriever
        self.llm = llm
        self.embedder = embedder
        self.profile = profile
        self.tools = tools
        self.verifier = verifier
        self.input_guard = input_guard
        self.privacy = privacy

    async def reply(
        self,
        session_id: str,
        user_text: str,
        channel: str,
        context: ChatContext,
    ) -> ChatResponse:
        user_text = user_text.strip()
        privacy_report = self.privacy.process(user_text)
        persisted_user_text = privacy_report.redacted_text
        security = self.input_guard.inspect(user_text, self.profile)
        if not security.allowed:
            response_text = security_refusal(security.category)
            self.db.add_message(
                session_id,
                "user",
                persisted_user_text,
                metadata={
                    "channel": channel,
                    "context": context.model_dump(),
                    "security": security.model_dump(),
                    "privacy": {
                        "detected_types": privacy_report.detected_types,
                        "redaction_count": privacy_report.redaction_count,
                    },
                },
            )
            self.db.add_message(
                session_id,
                "assistant",
                response_text,
                metadata={"security": security.model_dump()},
            )
            return ChatResponse(
                session_id=session_id,
                content=response_text,
                citations=[],
                actions=[
                    SuggestedAction(
                        type="escalate",
                        label=self.profile.tool_labels.get("contact", "Hablar con soporte humano"),
                        target=f"/v1/sessions/{session_id}/escalate",
                    )
                ],
                confidence=0.99,
                created_at=datetime.now(timezone.utc),
                provider=self.llm.provider_name,
                model=self.llm.model_name,
                security=security,
            )

        if self._is_courtesy(user_text):
            response_text = self._courtesy_response()
            actions = self._actions("")
            self.db.add_message(
                session_id,
                "user",
                persisted_user_text,
                metadata={
                    "channel": channel,
                    "context": context.model_dump(),
                    "privacy": {
                        "detected_types": privacy_report.detected_types,
                        "redaction_count": privacy_report.redaction_count,
                    },
                },
            )
            self.db.add_message(
                session_id,
                "assistant",
                response_text,
                metadata={
                    "actions": [item.model_dump() for item in actions],
                    "provider": self.llm.provider_name,
                    "model": self.llm.model_name,
                    "security": security.model_dump(),
                },
            )
            return ChatResponse(
                session_id=session_id,
                content=response_text,
                citations=[],
                actions=actions,
                confidence=0.9,
                created_at=datetime.now(timezone.utc),
                provider=self.llm.provider_name,
                model=self.llm.model_name,
                security=security,
            )

        citations = await self._citations(user_text)
        actions = self._actions(user_text)
        tool_results = []
        response_text = ""
        used_host = None
        confidence = 0.45
        provider = self.llm.provider_name
        model = self.llm.model_name

        intent = self._detect_intent(user_text)
        if must_abstain(intent, citations, self.profile.restricted_topics, user_text):
            response_text = abstention_message(self.profile)
            self._prepend_escalation(actions, session_id)
            confidence = 0.96
        elif intent == "escalation":
            tool_result = self.tools.for_intent(intent, user_text)
            if tool_result:
                tool_results.append(tool_result)
            response_text = (
                "Puedo derivarle a una persona del equipo de soporte. "
                "Si quiere, pulse el boton de contacto humano y adjuntare el contexto de esta conversacion."
            )
            actions.insert(
                0,
                SuggestedAction(
                    type="escalate",
                    label=self.profile.tool_labels.get("contact", "Contactar con una persona"),
                    target=f"/v1/sessions/{session_id}/escalate",
                ),
            )
            confidence = 0.93
        elif intent == "appointment":
            tool_result = self.tools.for_intent(intent, user_text)
            if tool_result:
                tool_results.append(tool_result)
            response_text = self._appointment_response(citations, tool_results)
            confidence = 0.84
        elif intent == "incident":
            tool_result = self.tools.for_intent(intent, user_text)
            if tool_result:
                tool_results.append(tool_result)
            response_text = self._incident_response(citations, tool_results)
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

        verification = self.verifier.verify(
            answer=response_text,
            citations=citations,
            tool_results=tool_results,
            requires_grounding=intent == "faq",
        )
        if self.settings.enable_answer_verification and not verification.grounded and intent == "faq":
            response_text = abstention_message(self.profile)
            self._prepend_escalation(actions, session_id)
            confidence = 0.97
            verification = self.verifier.verify(
                answer=response_text,
                citations=citations,
                tool_results=tool_results,
                requires_grounding=False,
            )

        self.db.add_message(
            session_id,
            "user",
            persisted_user_text,
            metadata={
                "channel": channel,
                "context": context.model_dump(),
                "privacy": {
                    "detected_types": privacy_report.detected_types,
                    "redaction_count": privacy_report.redaction_count,
                },
            },
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
                "tool_results": [item.model_dump() for item in tool_results],
                "verification": verification.model_dump(),
                "security": security.model_dump(),
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
            tool_results=tool_results,
            verification=verification,
            security=security,
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
                    build_system_prompt(self.settings, self.profile, context.easy_read)
                    + " "
                    + reading_style
                    + " No uses emojis."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{page_context}\n"
                    "Contexto oficial recuperado:\n"
                    + "\n".join(context_lines)
                    + f"\n\nPregunta ciudadana: {user_text}\n"
                    "Devuelve una respuesta breve y accionable. "
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
        citations: list[Citation] = []
        seen_sources: set[tuple[str, str]] = set()
        for chunk in chunks:
            source_key = (chunk.source, chunk.path)
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            citations.append(
                Citation(
                    source=chunk.source,
                    path=chunk.path,
                    snippet=self._clean_snippet(chunk.text),
                )
            )
            if len(citations) >= 3:
                break
        return citations

    def _actions(self, user_text: str) -> list[SuggestedAction]:
        text = user_text.lower()
        actions: list[SuggestedAction] = []
        if any(hint in text for hint in APPOINTMENT_HINTS):
            actions.append(
                SuggestedAction(
                    type="link",
                    label=self.profile.tool_labels.get("appointment", "Abrir reserva o cita"),
                    target=self.settings.appointment_url,
                )
            )
        if any(hint in text for hint in INCIDENT_HINTS):
            actions.append(
                SuggestedAction(
                    type="link",
                    label=self.profile.tool_labels.get("incident", "Registrar incidencia"),
                    target=self.settings.incidents_url,
                )
            )
        if not actions:
            actions.append(
                SuggestedAction(
                    type="link",
                    label=self.profile.tool_labels.get("contact", "Hablar con soporte humano"),
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

    def _is_courtesy(self, user_text: str) -> bool:
        text = user_text.lower().strip(" .,!¡¿?")
        return text in COURTESY_MESSAGES

    def _courtesy_response(self) -> str:
        if self.profile.organization_type == "hospital":
            return (
                "Perfecto. Puedo ayudarle con admision, cita previa, documentacion para una consulta "
                "o derivacion a personal del hospital. Si es una urgencia o una duda clinica, le indicare "
                "que contacte con un profesional sanitario."
            )
        return "Perfecto. Digame que necesita y le ayudo con el siguiente paso disponible."

    def _prepend_escalation(self, actions: list[SuggestedAction], session_id: str) -> None:
        if any(action.type == "escalate" for action in actions):
            return
        actions.insert(
            0,
            SuggestedAction(
                type="escalate",
                label=self.profile.tool_labels.get("contact", "Hablar con soporte humano"),
                target=f"/v1/sessions/{session_id}/escalate",
            ),
        )

    def _appointment_response(self, citations: list[Citation], tool_results: list) -> str:
        details = ""
        if citations:
            details = f" He localizado informacion relacionada en la fuente \"{citations[0].source}\"."
        tool_summary = f" {tool_results[0].summary}" if tool_results else ""
        return (
            "Puedo orientarle con la reserva o cita y llevarle al sistema correspondiente."
            f"{details}{tool_summary} Si me indica el servicio exacto, tambien puedo ayudarle a afinar la gestion antes de abrir la reserva."
        )

    def _incident_response(self, citations: list[Citation], tool_results: list) -> str:
        details = ""
        if citations:
            details = f" Tambien he encontrado referencia util en \"{citations[0].source}\"."
        tool_summary = f" {tool_results[0].summary}" if tool_results else ""
        return (
            "Para registrar una incidencia necesito al menos el tipo de problema y la ubicacion o contexto operativo."
            f"{details}{tool_summary} Puede continuar por aqui o abrir directamente el formulario de incidencias."
        )

    def _clean_snippet(self, text: str) -> str:
        cleaned = re.sub(r"`+", "", text)
        cleaned = cleaned.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:420]
