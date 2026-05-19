from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from app.llm import EmbeddingClient, chunk_fingerprint


WORD_RE = re.compile(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9]{2,}")
HEADING_RE = re.compile(r"^#+\s+")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


@dataclass(slots=True)
class Chunk:
    source: str
    path: str
    title: str
    text: str
    tokens: list[str]
    fingerprint: str
    vector: list[float] | None = None


class Retriever:
    def __init__(self, corpus_dir: Path, index_path: Path) -> None:
        self.corpus_dir = corpus_dir
        self.index_path = index_path
        self._chunks: list[Chunk] = []
        self._idf: dict[str, float] = {}

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    async def load(self, embedder: EmbeddingClient | None = None) -> None:
        chunks: list[Chunk] = []
        cached_vectors = self._read_index()
        for path in sorted(self.corpus_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            chunks.extend(self._split_markdown(path, text, cached_vectors))

        if embedder is not None:
            await self._populate_vectors(chunks, embedder)

        self._chunks = chunks
        self._idf = self._build_idf(chunks)
        self._write_index(chunks)

    async def reload(self, embedder: EmbeddingClient | None = None) -> None:
        await self.load(embedder)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        embedder: EmbeddingClient | None = None,
        lexical_weight: float = 0.45,
        semantic_weight: float = 0.55,
    ) -> list[Chunk]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_vector: list[float] | None = None
        if embedder is not None:
            vectors = await embedder.embed([query])
            if vectors and vectors[0]:
                query_vector = vectors[0]

        scored: list[tuple[float, Chunk]] = []
        for chunk in self._chunks:
            lexical_score = self._score_chunk(query_tokens, chunk)
            semantic_score = 0.0
            if query_vector and chunk.vector:
                semantic_score = _cosine_similarity(query_vector, chunk.vector)

            if query_vector and chunk.vector:
                score = lexical_weight * lexical_score + semantic_weight * semantic_score
            else:
                score = lexical_score

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    def _score_chunk(self, query_tokens: list[str], chunk: Chunk) -> float:
        chunk_freq: dict[str, int] = {}
        for token in chunk.tokens:
            chunk_freq[token] = chunk_freq.get(token, 0) + 1

        score = 0.0
        for token in query_tokens:
            tf = chunk_freq.get(token, 0)
            if not tf:
                continue
            idf = self._idf.get(token, 0.0)
            score += (1 + math.log(tf)) * idf

        if any(token in chunk.title.lower() for token in query_tokens):
            score *= 1.15
        return score

    def _build_idf(self, chunks: list[Chunk]) -> dict[str, float]:
        doc_count = max(1, len(chunks))
        docs_with_token: dict[str, int] = {}
        for chunk in chunks:
            for token in set(chunk.tokens):
                docs_with_token[token] = docs_with_token.get(token, 0) + 1

        return {
            token: math.log((doc_count + 1) / (count + 1)) + 1.0
            for token, count in docs_with_token.items()
        }

    def _split_markdown(
        self,
        path: Path,
        text: str,
        cached_vectors: dict[str, list[float]],
    ) -> list[Chunk]:
        blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
        chunks: list[Chunk] = []
        title = path.stem.replace("_", " ")
        current_heading = title

        for block in blocks:
            lines = block.splitlines()
            if lines and HEADING_RE.match(lines[0]):
                current_heading = HEADING_RE.sub("", lines[0]).strip()

            cleaned = " ".join(line.strip() for line in lines if line.strip())
            tokens = tokenize(cleaned)
            if len(tokens) < 8:
                continue

            fingerprint = chunk_fingerprint(f"{path}:{current_heading}:{cleaned}")
            chunks.append(
                Chunk(
                    source=current_heading,
                    path=str(path),
                    title=current_heading,
                    text=cleaned,
                    tokens=tokens,
                    fingerprint=fingerprint,
                    vector=cached_vectors.get(fingerprint),
                )
            )
        return chunks

    async def _populate_vectors(self, chunks: list[Chunk], embedder: EmbeddingClient) -> None:
        missing = [chunk for chunk in chunks if not chunk.vector]
        if not missing:
            return

        batch_size = 16
        for start in range(0, len(missing), batch_size):
            batch = missing[start : start + batch_size]
            vectors = await embedder.embed([chunk.text for chunk in batch])
            for chunk, vector in zip(batch, vectors, strict=False):
                chunk.vector = vector or None

    def _read_index(self) -> dict[str, list[float]]:
        if not self.index_path.exists():
            return {}
        try:
            payload = json.loads(self.index_path.read_text(encoding="utf-8"))
            return {key: value for key, value in payload.get("vectors", {}).items() if value}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_index(self, chunks: list[Chunk]) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "vectors": {chunk.fingerprint: chunk.vector for chunk in chunks if chunk.vector},
        }
        self.index_path.write_text(json.dumps(payload), encoding="utf-8")


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
