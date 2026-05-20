from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SessionCreateResponse(BaseModel):
    session_id: str
    welcome_message: str
    disclaimer: str
    city_name: str


class Citation(BaseModel):
    source: str
    path: str
    snippet: str


class SuggestedAction(BaseModel):
    type: Literal["link", "escalate", "intent", "tool"]
    label: str
    target: str


class ToolResult(BaseModel):
    name: str
    ok: bool
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    grounded: bool
    score: float
    reason: str
    unsupported_terms: list[str] = Field(default_factory=list)


class SecurityResult(BaseModel):
    allowed: bool
    category: str
    reason: str
    score: float = 0.0


class ChatContext(BaseModel):
    page_url: str | None = None
    geo: dict[str, Any] | None = None
    easy_read: bool = False


class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    channel: Literal["web", "mobile", "api"] = "web"
    context: ChatContext = Field(default_factory=ChatContext)


class ChatResponse(BaseModel):
    session_id: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    actions: list[SuggestedAction] = Field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime
    used_host: str | None = None
    provider: str | None = None
    model: str | None = None
    tool_results: list[ToolResult] = Field(default_factory=list)
    verification: VerificationResult | None = None
    security: SecurityResult | None = None


class FeedbackRequest(BaseModel):
    vote: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=1000)


class EscalationRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class DocumentUpsertRequest(BaseModel):
    filename: str = Field(min_length=3, max_length=150)
    content: str = Field(min_length=10, max_length=500_000)


class HistoryItem(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    created_at: datetime


class HistoryResponse(BaseModel):
    session_id: str
    items: list[HistoryItem]


class ToolInvokeRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    arguments: dict[str, Any] = Field(default_factory=dict)


class EvaluationRunResponse(BaseModel):
    total: int
    passed: int
    failed: int
    pass_rate: float
    failures: list[dict[str, Any]] = Field(default_factory=list)


class PrivacyExportResponse(BaseModel):
    session_id: str
    messages: list[HistoryItem]
    feedback: list[dict[str, Any]] = Field(default_factory=list)
    escalations: list[dict[str, Any]] = Field(default_factory=list)


class PrivacyActionResponse(BaseModel):
    status: str
    session_id: str | None = None
    affected_rows: int = 0
    detail: str = ""


class PrivacyScanResponse(BaseModel):
    redacted_text: str
    detected_types: list[str] = Field(default_factory=list)
    redaction_count: int = 0


class SpeechSynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1500)


class SpeechTranscriptionResponse(BaseModel):
    text: str
    language: str


class DocumentIntakeResponse(BaseModel):
    document_ref: str
    filename: str
    content_type: str | None = None
    size_bytes: int
