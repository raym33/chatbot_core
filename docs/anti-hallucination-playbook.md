# Anti-Hallucination Playbook

## Working Principle

The target is not to promise zero hallucinations.

The target is to build a system that:

- answers from evidence,
- cites or traces that evidence,
- abstains when support is weak,
- escalates sensitive requests,
- exposes regressions through evaluation.

## Techniques By Layer

| Layer | Technique | Why it matters | Status |
|---|---|---|---|
| Ingestion | Corpus normalization and versioning | Reduces duplicate, stale, or conflicting sources | Base implementation |
| Retrieval | Hybrid lexical + semantic RAG | Balances exact matches and semantic recall | Implemented |
| Retrieval | Reranking | Improves evidence ordering before generation | Planned |
| Generation | Citation support | Makes answers easier to audit | Implemented |
| Generation | Abstention on weak support | Avoids unsupported factual claims | Implemented |
| Verification | Grounding verifier | Checks whether answer support is sufficient | Implemented |
| Security | Prompt injection guard | Prevents instruction hijacking | Implemented |
| Security | Rate limiting | Reduces abuse and overload | Implemented |
| Evaluation | Golden set | Catches retrieval regressions before release | Implemented |
| Evaluation | Local LLM judge | Adds second-pass factuality checks | Planned |
| Operations | Human handoff | Handles low-confidence or high-risk cases | Stub included |

## Domain Guidance

| Domain | Default posture |
|---|---|
| Hospital | Abstain on symptoms, diagnosis, prescriptions, or emergency triage |
| City hall | Abstain on deadlines, requirements, fees, or decisions without explicit source support |
| Enterprise | Abstain on prices, contracts, commitments, or security-sensitive facts without evidence |
| Internal support | Prefer KB or tools; otherwise create or escalate a ticket |

## Golden Rule

The model should not be treated as the database.

The model writes. Retrieval and tools provide the evidence.
