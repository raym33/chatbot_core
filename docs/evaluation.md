# Evaluation

## What Is Evaluated First

The first evaluation target is retrieval quality, not answer style.

If the system cannot reliably retrieve the right evidence, downstream generation quality is not meaningful.

## Golden Set

The baseline dataset lives at:

```text
datasets/evaluation/golden_general_es.jsonl
```

Each entry contains:

- `id`
- `question`
- `must_retrieve`
- `forbidden_answer_terms`

The current script focuses on whether the retriever surfaces the required evidence for each test question.

## Running The Evaluation

```bash
source .venv/bin/activate
python scripts/evaluate_golden_set.py
```

There is also an API endpoint for retrieval evaluation:

```bash
curl -X POST http://127.0.0.1:8000/v1/admin/evaluations/retrieval
```

## Why This Matters

This repository is meant to show that:

- retrieval can be validated automatically,
- safety behavior can be tested,
- structural regressions in sector packs can be caught early,
- grounding quality can be tracked over time.

## Recommended Extensions

- Domain-specific golden sets.
- Nightly regression jobs.
- Citation coverage checks per sentence.
- Local LLM-as-judge for factuality and tone.
- Separate thresholds by domain risk level.
