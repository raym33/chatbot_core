# Security, Abuse, and Prompt Injection

## Threats Addressed

| Threat | Risk | Current mitigation |
|---|---|---|
| Prompt injection | Override internal rules or redirect the assistant | `InputGuard` in `app/security.py` |
| System prompt leakage | Exposure of hidden instructions | Pattern-based blocking and no secrets in prompts |
| Unbounded consumption | Excessive cost or instability | Rate limiting and payload limits |
| Out-of-domain traffic | Low-value load and unreliable answers | Optional `strict_domain_guard` |
| Tool abuse | Unsafe or excessive tool execution | Controlled tool registry and explicit stubs |
| Retrieval poisoning | Malicious or stale source material | Corpus versioning and evaluation workflow |
| WebSocket abuse | Oversized messages or loop-based load | Message size constraints |

## Important Runtime Controls

| Variable | Default | Purpose |
|---|---:|---|
| `MUNIBOT_MAX_MESSAGE_CHARS` | `4000` | Maximum user message length |
| `MUNIBOT_REQUEST_BODY_LIMIT_BYTES` | `4000000` | Maximum HTTP body size |
| `MUNIBOT_REQUESTS_PER_MINUTE` | `90` | Basic per-IP rate limit |
| `MUNIBOT_STRICT_DOMAIN_GUARD` | `false` | Hard reject for out-of-domain queries |
| `MUNIBOT_ENABLE_ANSWER_VERIFICATION` | `true` | Enables grounding verification hooks |

## Production Recommendations

For real deployments, move these controls into shared infrastructure:

- edge rate limiting with `NGINX`, `Envoy`, `Traefik`, or `Kong`,
- distributed counters with `Redis`,
- WAF rules for abusive LLM traffic,
- per-session concurrency limits,
- authenticated tools for any side-effectful action.

## OWASP LLM Mapping

| OWASP category | Control direction |
|---|---|
| LLM01 Prompt Injection | Input guards, context separation, explicit tool allowlists |
| LLM02 Sensitive Information Disclosure | No secrets in prompts, privacy redaction |
| LLM05 Improper Output Handling | Structured outputs and verification hooks |
| LLM06 Excessive Agency | Constrained tools and no irreversible auto-actions |
| LLM07 System Prompt Leakage | Exfiltration resistance and minimal hidden instructions |
| LLM08 Vector And Embedding Weaknesses | Retrieval evaluation and corpus governance |
| LLM09 Misinformation | RAG, citations, abstention, golden sets |
| LLM10 Unbounded Consumption | Rate limits, payload limits, bounded sessions |
