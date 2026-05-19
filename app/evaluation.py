from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.llm import NullEmbeddingClient
from app.models import EvaluationRunResponse
from app.rag import Retriever


@dataclass(slots=True)
class GoldenCase:
    id: str
    question: str
    must_retrieve: list[str]
    forbidden_answer_terms: list[str]


def load_golden_set(path: Path) -> list[GoldenCase]:
    cases: list[GoldenCase] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        payload = json.loads(raw)
        cases.append(
            GoldenCase(
                id=payload["id"],
                question=payload["question"],
                must_retrieve=payload.get("must_retrieve", []),
                forbidden_answer_terms=payload.get("forbidden_answer_terms", []),
            )
        )
    return cases


async def run_retrieval_evaluation(
    retriever: Retriever,
    golden_path: Path,
    top_k: int = 5,
) -> EvaluationRunResponse:
    cases = load_golden_set(golden_path)
    failures: list[dict[str, Any]] = []
    embedder = NullEmbeddingClient()

    for case in cases:
        chunks = await retriever.search(case.question, top_k=top_k, embedder=embedder)
        haystack = " ".join(f"{chunk.title} {chunk.text}" for chunk in chunks).lower()
        missing = [term for term in case.must_retrieve if term.lower() not in haystack]
        if missing:
            failures.append(
                {
                    "id": case.id,
                    "question": case.question,
                    "missing": missing,
                    "retrieved": [chunk.title for chunk in chunks],
                }
            )

    total = len(cases)
    failed = len(failures)
    passed = total - failed
    pass_rate = passed / total if total else 0.0
    return EvaluationRunResponse(
        total=total,
        passed=passed,
        failed=failed,
        pass_rate=round(pass_rate, 3),
        failures=failures,
    )
