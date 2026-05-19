from __future__ import annotations

import re

from app.models import Citation, ToolResult, VerificationResult
from app.rag import tokenize


STOPWORDS = {
    "para",
    "como",
    "esta",
    "este",
    "estos",
    "estas",
    "puede",
    "puedo",
    "debe",
    "deben",
    "sobre",
    "segun",
    "entre",
    "tambien",
    "informacion",
    "respuesta",
    "servicio",
    "soporte",
}


class GroundingVerifier:
    def __init__(self, min_grounding_score: float = 0.18) -> None:
        self.min_grounding_score = min_grounding_score

    def verify(
        self,
        answer: str,
        citations: list[Citation],
        tool_results: list[ToolResult],
        requires_grounding: bool = True,
    ) -> VerificationResult:
        if not requires_grounding:
            return VerificationResult(grounded=True, score=1.0, reason="No requiere grounding factual.")

        support_text = " ".join(citation.snippet for citation in citations)
        support_text += " " + " ".join(result.summary for result in tool_results if result.ok)
        support_tokens = set(_content_tokens(support_text))
        answer_tokens = _content_tokens(answer)

        if not answer_tokens:
            return VerificationResult(
                grounded=False,
                score=0.0,
                reason="Respuesta vacia.",
                unsupported_terms=[],
            )

        supported = [token for token in answer_tokens if token in support_tokens]
        score = len(supported) / max(1, len(set(answer_tokens)))
        unsupported = sorted({token for token in answer_tokens if token not in support_tokens})[:12]

        grounded = bool(citations or tool_results) and score >= self.min_grounding_score
        reason = (
            "Respuesta suficientemente apoyada por fuentes o herramientas."
            if grounded
            else "Grounding insuficiente; conviene abstenerse o escalar."
        )
        return VerificationResult(
            grounded=grounded,
            score=round(score, 3),
            reason=reason,
            unsupported_terms=unsupported,
        )


def _content_tokens(text: str) -> list[str]:
    tokens = tokenize(re.sub(r"https?://\S+", " ", text))
    return [token for token in tokens if len(token) > 3 and token not in STOPWORDS]
