from __future__ import annotations

import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.chat import ChatService
from app.config import get_settings
from app.db import Database
from app.domain import DomainProfile
from app.llm import (
    LMStudioChatClient,
    LMStudioEmbeddingClient,
    NullEmbeddingClient,
    OllamaClusterClient,
    OllamaEmbeddingClient,
)
from app.models import (
    DocumentUpsertRequest,
    EscalationRequest,
    EvaluationRunResponse,
    FeedbackRequest,
    HistoryItem,
    HistoryResponse,
    MessageRequest,
    SessionCreateResponse,
    ToolInvokeRequest,
)
from app.rag import Retriever
from app.evaluation import run_retrieval_evaluation
from app.security import InMemoryRateLimitMiddleware, InputGuard
from app.tools import ToolRegistry
from app.verifier import GroundingVerifier


settings = get_settings()
db = Database(settings.db_path)
retriever = Retriever(settings.corpus_dir, settings.rag_index_path)
if settings.domain_profile_path and settings.domain_profile_path.exists():
    profile = DomainProfile.from_file(settings.domain_profile_path)
else:
    profile = DomainProfile.default(
        organization_name=settings.effective_organization_name,
        organization_type=settings.organization_type,
    )

if settings.ai_backend == "lmstudio":
    llm = LMStudioChatClient(
        settings.lmstudio_base_url, settings.lmstudio_chat_model, settings.llm_timeout_seconds
    )
    embedder = LMStudioEmbeddingClient(
        settings.lmstudio_base_url, settings.lmstudio_embed_model, settings.llm_timeout_seconds
    )
else:
    llm = OllamaClusterClient(
        settings.ollama_hosts, settings.ollama_chat_model, settings.llm_timeout_seconds
    )
    embedder = OllamaEmbeddingClient(
        settings.ollama_hosts, settings.ollama_embed_model, settings.llm_timeout_seconds
    )

if not settings.enable_semantic_rag:
    embedder = NullEmbeddingClient()

tools = ToolRegistry(settings, profile)
verifier = GroundingVerifier(min_grounding_score=settings.min_grounding_score)
input_guard = InputGuard(
    max_message_chars=settings.max_message_chars,
    strict_domain=settings.strict_domain_guard,
)
chat_service = ChatService(settings, db, retriever, llm, embedder, profile, tools, verifier, input_guard)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init()
    settings.corpus_dir.mkdir(parents=True, exist_ok=True)
    await retriever.load(embedder if settings.enable_semantic_rag else None)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    InMemoryRateLimitMiddleware,
    requests_per_minute=settings.requests_per_minute,
    request_body_limit_bytes=settings.request_body_limit_bytes,
    exempt_paths={"/", "/v1/health"},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "demo.html")


@app.get("/v1/health")
async def health() -> dict[str, object]:
    return {
        "ok": True,
        "city": settings.city_name,
        "organization": profile.name,
        "corpus_chunks": retriever.chunk_count,
        "provider": settings.ai_backend,
        "chat_model": settings.chat_model,
        "embed_model": settings.embed_model,
    }


@app.get("/v1/cluster")
async def cluster() -> dict[str, object]:
    return {
        "nodes": await llm.health(),
        "embedding_nodes": await embedder.health(),
        "model": settings.chat_model,
        "embedding_model": settings.embed_model,
        "provider": settings.ai_backend,
        "profile": profile.organization_type,
    }


@app.get("/v1/tools")
async def list_tools() -> dict[str, object]:
    return {"tools": tools.list_tools(), "profile": profile.organization_type}


@app.post("/v1/tools/invoke")
async def invoke_tool(payload: ToolInvokeRequest):
    return tools.invoke(payload.name, payload.arguments)


@app.post("/v1/sessions", response_model=SessionCreateResponse)
async def create_session() -> SessionCreateResponse:
    session_id = db.create_session()
    return SessionCreateResponse(
        session_id=session_id,
        welcome_message="Hola. Estoy listo para ayudarle con informacion, reservas, incidencias o soporte segun el dominio configurado.",
        disclaimer="Esta conversando con una IA asistida por documentos y reglas de seguridad. Si falta soporte verificable, la respuesta debe abstenerse o escalar.",
        city_name=profile.name,
    )


@app.post("/v1/sessions/{session_id}/messages")
async def send_message(session_id: str, payload: MessageRequest):
    _require_session(session_id)
    return await chat_service.reply(session_id, payload.content, payload.channel, payload.context)


@app.get("/v1/sessions/{session_id}/history", response_model=HistoryResponse)
async def history(session_id: str) -> HistoryResponse:
    _require_session(session_id)
    items = [
        HistoryItem(role=row["role"], content=row["content"], created_at=row["created_at"])
        for row in db.history(session_id)
    ]
    return HistoryResponse(session_id=session_id, items=items)


@app.post("/v1/sessions/{session_id}/feedback")
async def feedback(session_id: str, payload: FeedbackRequest) -> dict[str, str]:
    _require_session(session_id)
    db.add_feedback(session_id, payload.vote, payload.comment)
    return {"status": "ok"}


@app.post("/v1/sessions/{session_id}/escalate")
async def escalate(session_id: str, payload: EscalationRequest) -> dict[str, str]:
    _require_session(session_id)
    ticket_id = db.add_escalation(session_id, payload.reason)
    return {"status": "queued", "ticket_id": ticket_id, "handoff_url": settings.human_handoff_url}


@app.post("/v1/admin/reload-corpus")
async def reload_corpus() -> dict[str, object]:
    await retriever.reload(embedder if settings.enable_semantic_rag else None)
    return {"status": "ok", "chunks": retriever.chunk_count}


@app.post("/v1/admin/documents")
async def upsert_document(payload: DocumentUpsertRequest) -> dict[str, object]:
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", payload.filename).strip("._")
    if not safe_name.endswith(".md"):
        safe_name += ".md"
    target = settings.corpus_dir / safe_name
    target.write_text(payload.content, encoding="utf-8")
    await retriever.reload(embedder if settings.enable_semantic_rag else None)
    return {"status": "ok", "path": str(target), "chunks": retriever.chunk_count}


@app.post("/v1/admin/evaluations/retrieval", response_model=EvaluationRunResponse)
async def evaluate_retrieval() -> EvaluationRunResponse:
    if not settings.golden_set_path.exists():
        raise HTTPException(status_code=404, detail="golden set not found")
    return await run_retrieval_evaluation(retriever, settings.golden_set_path, top_k=settings.top_k)


@app.websocket("/v1/sessions/{session_id}/stream")
async def stream(session_id: str, websocket: WebSocket) -> None:
    if not db.ensure_session(session_id):
        await websocket.close(code=4404, reason="unknown session")
        return

    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            if len(raw) > settings.request_body_limit_bytes:
                await websocket.close(code=1009, reason="message too large")
                return
            payload = MessageRequest.model_validate(json.loads(raw))
            response = await chat_service.reply(session_id, payload.content, payload.channel, payload.context)
            for token in _token_stream(response.content):
                await websocket.send_json({"type": "token", "text": token})
            for citation in response.citations:
                await websocket.send_json({"type": "citation", "data": citation.model_dump()})
            for action in response.actions:
                await websocket.send_json({"type": "action", "data": action.model_dump()})
            await websocket.send_json(
                {
                    "type": "done",
                    "data": {
                        "confidence": response.confidence,
                        "used_host": response.used_host,
                    },
                }
            )
    except WebSocketDisconnect:
        return


def _require_session(session_id: str) -> None:
    if not db.ensure_session(session_id):
        raise HTTPException(status_code=404, detail="session not found")


def _token_stream(text: str) -> list[str]:
    return re.findall(r"\S+\s*", text)
