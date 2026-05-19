from __future__ import annotations

import re
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.domain import DomainProfile
from app.models import SecurityResult


PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) (instructions|rules)",
    r"olvida (todas )?(las )?(instrucciones|reglas) anteriores",
    r"revela (el )?(prompt|system prompt|mensaje del sistema)",
    r"show (me )?(the )?(system prompt|developer message|hidden instructions)",
    r"actua como dan|do anything now",
    r"jailbreak|prompt injection",
    r"exfiltra|exfiltrate|filtra el prompt",
    r"imprime tus instrucciones",
    r"base64.*(prompt|instrucciones|system)",
]

ABUSE_PATTERNS = [
    r"(repite|repeat).{0,40}(\d{4,}|infinit)",
    r"(genera|generate).{0,40}(millones|millions|100000)",
    r"while true|fork bomb|denial of service|ataque ddos",
]


class InputGuard:
    def __init__(self, max_message_chars: int, strict_domain: bool = False) -> None:
        self.max_message_chars = max_message_chars
        self.strict_domain = strict_domain

    def inspect(self, user_text: str, profile: DomainProfile) -> SecurityResult:
        text = user_text.strip()
        lowered = text.lower()
        if len(text) > self.max_message_chars:
            return SecurityResult(
                allowed=False,
                category="oversized_input",
                reason="La entrada supera el limite permitido.",
                score=1.0,
            )
        if _matches(lowered, PROMPT_INJECTION_PATTERNS):
            return SecurityResult(
                allowed=False,
                category="prompt_injection",
                reason="La entrada intenta modificar o revelar instrucciones internas.",
                score=0.95,
            )
        if _matches(lowered, ABUSE_PATTERNS):
            return SecurityResult(
                allowed=False,
                category="resource_abuse",
                reason="La entrada parece orientada a consumir recursos de forma abusiva.",
                score=0.9,
            )
        if self.strict_domain and _looks_out_of_scope(lowered, profile):
            return SecurityResult(
                allowed=False,
                category="out_of_scope",
                reason="La consulta no parece pertenecer al dominio configurado.",
                score=0.75,
            )
        return SecurityResult(allowed=True, category="clean", reason="Entrada aceptada.", score=0.0)


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int,
        request_body_limit_bytes: int,
        exempt_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_body_limit_bytes = request_body_limit_bytes
        self.exempt_paths = exempt_paths or set()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.exempt_paths or request.url.path.startswith("/static"):
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.request_body_limit_bytes:
            return JSONResponse(
                {"detail": "request body too large"},
                status_code=413,
            )

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._hits[client]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= self.requests_per_minute:
            return JSONResponse(
                {"detail": "rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "60"},
            )
        window.append(now)
        return await call_next(request)


def security_refusal(category: str) -> str:
    if category == "prompt_injection":
        return (
            "No puedo seguir instrucciones que intenten cambiar mis reglas internas o revelar mensajes del sistema. "
            "Puedo ayudarle con una consulta dentro del dominio configurado."
        )
    if category == "resource_abuse":
        return (
            "No puedo ejecutar solicitudes orientadas a consumir recursos de forma abusiva. "
            "Puedo responder una consulta concreta y acotada."
        )
    if category == "out_of_scope":
        return "Esa consulta no parece pertenecer al ambito de este asistente. Puedo ayudarle con el dominio configurado."
    return "No puedo procesar esa entrada con seguridad. Reformule la consulta de forma mas concreta."


def _matches(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _looks_out_of_scope(text: str, profile: DomainProfile) -> bool:
    domain_terms = {
        "cityhall": ["tramite", "cita", "incidencia", "ayuntamiento", "sede", "padron"],
        "hospital": ["cita", "paciente", "hospital", "admision", "prueba", "consulta"],
        "company": ["soporte", "ticket", "producto", "factura", "contrato", "demo"],
        "general": [],
    }
    terms = domain_terms.get(profile.organization_type, [])
    if not terms:
        return False
    return not any(term in text for term in terms)
