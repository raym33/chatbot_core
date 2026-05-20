# Architecture Overview

## Purpose

`chatbot_core` is a reference implementation for grounded assistants that combine:

- local or self-hosted LLM inference,
- document retrieval,
- domain-specific policies,
- live tool integrations,
- safety and privacy controls.

The goal is not to maximize answer coverage at any cost. The goal is to keep the assistant useful while making unsupported answers less likely.

## Main Components

- `app/main.py`
  REST and WebSocket API, session lifecycle, streaming, audio endpoints, and admin routes.
- `app/chat.py`
  Conversation orchestration, retrieval injection, citation shaping, abstention behavior, and action suggestions.
- `app/rag.py`
  Lightweight hybrid retrieval over Markdown corpora with lexical scoring and optional embedding vectors.
- `app/llm.py`
  Client adapters for `LM Studio` and `Ollama` for both generation and embeddings.
- `app/policy.py`
  Domain boundaries, safety rules, and escalation logic.
- `app/security.py`
  Request constraints, prompt injection resistance hooks, and abuse controls.
- `app/privacy.py`
  PII redaction, retention, export, deletion, and anonymization utilities.
- `app/speech.py`
  `Whisper` transcription and `edge-tts` speech synthesis.
- `app/static/munibot.js`
  Embeddable widget with streaming UI and continuous voice mode.

## Request Flow

1. The widget creates or resumes a session.
2. The backend retrieves relevant chunks from the configured corpus.
3. A prompt is assembled with domain context, citations, and policy constraints.
4. The selected LLM generates the answer.
5. The backend streams text, citations, and suggested actions back to the client.
6. If enabled, the response is also synthesized to speech.

## Retrieval Strategy

The RAG layer is intentionally simple and inspectable:

- Markdown files are split into chunks.
- Lexical retrieval uses in-memory token statistics.
- Semantic retrieval is added when embeddings are available.
- Hybrid scores are fused with configurable weights.
- Cached vectors are stored in `data/rag_index.json`.

This keeps the retrieval path easy to review in a prototype while still supporting semantic grounding.

## Inference Strategy

Two backends are supported:

- `LM Studio`
  Best for local prototyping, model switching, and OpenAI-compatible serving.
- `Ollama`
  Best for simple worker nodes and lightweight distributed inference.

The backend can be selected through environment variables without changing application code.

## Domain Adaptation

The repository separates common orchestration from domain behavior:

- `profiles/` define lightweight domain configuration.
- `skills/` define sector packs with intents, rules, golden sets, and fine-tuning seeds.
- `mcps/` define integration contracts for external systems.

This makes it possible to reuse the same core across hospitals, municipalities, enterprise support, finance, legal, and other domains.

## Design Principles

- Retrieval for facts.
- Fine-tuning for behavior.
- Tools for live data and side effects.
- Verification and abstention when evidence is weak.
- Escalation for sensitive or high-risk cases.
