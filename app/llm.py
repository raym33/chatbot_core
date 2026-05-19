from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


@dataclass(slots=True)
class LLMResult:
    text: str
    host: str | None
    model: str | None = None
    provider: str | None = None


class ChatClient(Protocol):
    model_name: str
    provider_name: str

    async def health(self) -> list[dict[str, Any]]: ...

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult: ...


class EmbeddingClient(Protocol):
    model_name: str
    provider_name: str

    async def health(self) -> list[dict[str, Any]]: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class NullEmbeddingClient:
    model_name = "disabled"
    provider_name = "none"

    async def health(self) -> list[dict[str, Any]]:
        return [{"provider": self.provider_name, "ok": True, "model": self.model_name}]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[] for _ in texts]


class OllamaClusterClient:
    provider_name = "ollama"

    def __init__(self, hosts: list[str], model: str, timeout_seconds: float) -> None:
        self.hosts = hosts
        self.model_name = model
        self.timeout_seconds = timeout_seconds
        self._round_robin = itertools.cycle(hosts) if hosts else None

    async def health(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=5.0) as client:
            for host in self.hosts:
                ok = False
                try:
                    response = await client.get(f"{host}/api/tags")
                    ok = response.status_code == 200
                except httpx.HTTPError:
                    ok = False
                results.append(
                    {
                        "provider": self.provider_name,
                        "host": host,
                        "ok": ok,
                        "model": self.model_name,
                    }
                )
        return results

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult:
        if not self._round_robin:
            return LLMResult(text="", host=None, model=self.model_name, provider=self.provider_name)

        tried: set[str] = set()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            while len(tried) < len(self.hosts):
                host = next(self._round_robin)
                if host in tried:
                    continue
                tried.add(host)
                try:
                    response = await client.post(
                        f"{host}/api/chat",
                        json={
                            "model": self.model_name,
                            "stream": False,
                            "messages": messages,
                            "options": {
                                "temperature": 0.2,
                                "num_predict": 450,
                            },
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()
                    content = payload.get("message", {}).get("content", "").strip()
                    if content:
                        return LLMResult(
                            text=content,
                            host=host,
                            model=self.model_name,
                            provider=self.provider_name,
                        )
                except httpx.HTTPError:
                    continue

        return LLMResult(text="", host=None, model=self.model_name, provider=self.provider_name)


class OllamaEmbeddingClient:
    provider_name = "ollama"

    def __init__(self, hosts: list[str], model: str, timeout_seconds: float) -> None:
        self.hosts = hosts
        self.model_name = model
        self.timeout_seconds = timeout_seconds
        self._round_robin = itertools.cycle(hosts) if hosts else None

    async def health(self) -> list[dict[str, Any]]:
        return await OllamaClusterClient(self.hosts, self.model_name, self.timeout_seconds).health()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self._round_robin:
            return [[] for _ in texts]

        tried: set[str] = set()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            while len(tried) < len(self.hosts):
                host = next(self._round_robin)
                if host in tried:
                    continue
                tried.add(host)
                try:
                    response = await client.post(
                        f"{host}/api/embed",
                        json={"model": self.model_name, "input": texts},
                    )
                    response.raise_for_status()
                    payload = response.json()
                    vectors = payload.get("embeddings", [])
                    if vectors:
                        return vectors
                except httpx.HTTPError:
                    continue
        return [[] for _ in texts]


class LMStudioChatClient:
    provider_name = "lmstudio"

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model
        self.timeout_seconds = timeout_seconds

    async def health(self) -> list[dict[str, Any]]:
        ok = False
        model_found = False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                data = response.json().get("data", [])
                model_found = any(item.get("id") == self.model_name for item in data)
                ok = True
        except httpx.HTTPError:
            ok = False
        return [
            {
                "provider": self.provider_name,
                "host": self.base_url,
                "ok": ok,
                "model": self.model_name,
                "model_found": model_found,
            }
        ]

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model_name,
                        "temperature": 0.2,
                        "messages": messages,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
                return LLMResult(
                    text=content.strip(),
                    host=self.base_url,
                    model=self.model_name,
                    provider=self.provider_name,
                )
        except httpx.HTTPError:
            return LLMResult(text="", host=self.base_url, model=self.model_name, provider=self.provider_name)


class LMStudioEmbeddingClient:
    provider_name = "lmstudio"

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model
        self.timeout_seconds = timeout_seconds

    async def health(self) -> list[dict[str, Any]]:
        return await LMStudioChatClient(self.base_url, self.model_name, self.timeout_seconds).health()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    json={"model": self.model_name, "input": texts},
                )
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data", [])
                vectors = [item.get("embedding", []) for item in data]
                if vectors:
                    return vectors
        except httpx.HTTPError:
            pass
        return [[] for _ in texts]


def chunk_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
