# Chatbot Core

`chatbot_core` is a technical prototype for building grounded, domain-adaptable assistants on top of open-source LLMs.

The project is designed to demonstrate:

- hybrid RAG over local documentation,
- configurable inference backends (`LM Studio` and `Ollama`),
- domain policies and abstention behavior,
- tool calling for live actions,
- voice input/output with `Whisper` and `edge-tts`,
- security and privacy controls,
- repeatable evaluation for retrieval quality.

The repository is intentionally organized as a reusable platform rather than a single vertical demo.

## Technical Goals

- Minimize hallucinations through retrieval, verification, and abstention-first policies.
- Separate static knowledge, live data, and model behavior.
- Support multiple sectors through domain packs instead of hard-coding one chatbot.
- Keep the stack self-hostable and easy to inspect for engineering review.

## Core Capabilities

- `FastAPI` backend with session management, streaming responses, escalation hooks, and admin endpoints.
- Hybrid retrieval layer: lexical scoring plus optional embedding-based semantic ranking.
- Configurable LLM clients for `LM Studio` and `Ollama`.
- Embeddable web widget based on `Shadow DOM`.
- Voice conversation loop with silence detection, `Whisper` STT, and `edge-tts` TTS.
- Policy layer for abstention, domain restrictions, clinical/legal/financial safety boundaries, and prompt injection resistance.
- Privacy helpers for PII redaction, retention, and data export/delete flows.
- Sector packs in `skills/` with intents, tool contracts, golden sets, and fine-tuning seeds.
- MCP-style integration manifests in `mcps/` for CRM, ERP, HIS, OCR, ticketing, GIS, and appointment systems.

## Architecture

The platform follows a layered approach:

1. `RAG` for factual grounding.
2. `Fine-tuning` for behavior, tone, and refusal patterns.
3. `Tools / APIs` for volatile or transactional data.
4. `Verification + abstention` when evidence is weak or missing.

This repository does not claim that hallucinations can be reduced to absolute zero. It is built to make unsupported answers less likely, easier to detect, and easier to escalate safely.

## Repository Layout

```text
app/              FastAPI app, RAG, policies, security, privacy, audio, tools
data/             Sample corpora and local runtime folders
datasets/         Evaluation and fine-tuning seed datasets
deploy/           Generic deployment templates and cluster examples
docs/             Technical notes on architecture, deployment, evaluation, safety
mcps/             Integration manifests and connector contracts
profiles/         Domain configuration profiles
scripts/          Bootstrap, evaluation, validation, and cluster helper scripts
skills/           Sector packs with rules, intents, examples, and tests
tests/            Unit tests for retrieval, tools, privacy, verification, and security
```

## Quickstart

### 1. Bootstrap the project

```bash
bash scripts/bootstrap.sh
```

This script:

- creates `.venv` if needed,
- installs the project in editable mode,
- installs development dependencies,
- creates `.env` from `.env.example` if missing,
- prepares local runtime directories.

### 2. Configure the environment

Edit `.env` and select one backend:

- `LM Studio` for a local OpenAI-compatible server, or
- `Ollama` for one or more local/network workers.

Minimum settings:

```env
MUNIBOT_AI_BACKEND=lmstudio
MUNIBOT_ORGANIZATION_NAME=Example Organization
MUNIBOT_ORGANIZATION_TYPE=company
MUNIBOT_DOMAIN_PROFILE_PATH=profiles/company.json
MUNIBOT_CORPUS_DIR=data/corpus
```

### 3. Run the API

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open the demo UI

```text
http://localhost:8000/static/demo.html
```

## Inference Backends

### LM Studio

Recommended when you want:

- a simple local OpenAI-compatible endpoint,
- quick model swaps during prototyping,
- a single-node authoring or demo workflow.

Relevant settings:

```env
MUNIBOT_AI_BACKEND=lmstudio
MUNIBOT_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
MUNIBOT_LMSTUDIO_CHAT_MODEL=gemma-4-26b-a4b-it-mlx
MUNIBOT_LMSTUDIO_EMBED_MODEL=text-embedding-nomic-embed-text-v1.5
```

### Ollama

Recommended when you want:

- lightweight worker nodes,
- distributed inference over multiple hosts,
- simpler node-level operations.

Relevant settings:

```env
MUNIBOT_AI_BACKEND=ollama
MUNIBOT_OLLAMA_HOSTS_RAW=http://worker-a.internal:11434,http://worker-b.internal:11434
MUNIBOT_OLLAMA_CHAT_MODEL=qwen3.5:9b
MUNIBOT_OLLAMA_EMBED_MODEL=bge-m3
```

## Voice Pipeline

The widget supports full speech interaction:

- `POST /v1/audio/transcriptions` for local STT via `Whisper`
- `POST /v1/audio/speech` for TTS via `edge-tts`

The browser widget includes a continuous voice mode:

- one click to start listening,
- automatic silence detection,
- transcription and response generation,
- spoken answer playback,
- automatic return to listening,
- explicit stop button to end the loop.

## Domain Adaptation

The codebase is split into `core + sector packs`.

Each sector pack can include:

- `profile.json`
- `SKILL.md`
- `intents.json`
- `tools.json`
- `golden_set.jsonl`
- `fine_tuning_seed.jsonl`
- `README.md`

Initial packs are included for:

- hospitals,
- medium city halls,
- insurance agencies,
- legal offices,
- financial advisors,
- tractor sales,
- dental clinics,
- aesthetic clinics,
- mechanic workshops.

The repository also includes a working hospital reference vertical with demo connectors for appointments, admission status, handoff, and OCR:

- `docs/hospital-reference-vertical.md`

## Anti-Hallucination Strategy

The prototype uses multiple complementary controls:

- retrieval-first answering,
- optional semantic reranking,
- minimum grounding thresholds,
- domain guards,
- abstention when evidence is insufficient,
- safety-oriented system prompts,
- tool routing for live data,
- output verification hooks,
- golden-set evaluation for retrieval regressions.

See also:

- `docs/hallucination-control.md`
- `docs/anti-hallucination-playbook.md`
- `docs/security-and-abuse.md`

## Evaluation

Run the core checks with:

```bash
source .venv/bin/activate
ruff check
pytest
python scripts/evaluate_golden_set.py
python scripts/validate_sector_packs.py
```

What this demonstrates to a reviewer:

- retrieval quality can be measured,
- sector packs can be validated structurally,
- safety/privacy logic is covered by tests,
- the prototype is meant to be inspected, not just demoed.

## Useful Scripts

- `bash scripts/bootstrap.sh`
- `bash scripts/run_gateway.sh`
- `bash scripts/run_ollama_node.sh`
- `python scripts/check_ollama_nodes.py`
- `python scripts/evaluate_golden_set.py`
- `python scripts/build_finetune_seed_dataset.py`
- `python scripts/validate_finetune_dataset.py datasets/fine_tuning/seed_general_es.jsonl`
- `python scripts/validate_sector_packs.py`
- `python scripts/deploy_cluster.py`

## Notes For Reviewers

- The sample corpus is intentionally local and file-based to keep the prototype easy to run and inspect.
- Domain packs illustrate how the same core can be constrained differently across sectors.
- Fine-tuning is included as a structure and workflow, not as a replacement for RAG.
- The code favors explicit safety boundaries over maximal answer coverage.

## License

MIT. See `LICENSE`.
