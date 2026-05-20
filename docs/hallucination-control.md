# Hallucination Control

## Practical Position

Absolute zero hallucinations cannot be guaranteed with a generative model.

What can be engineered is a stack that:

- grounds factual answers in retrieval,
- refuses when evidence is missing,
- routes volatile questions to tools,
- escalates high-risk cases,
- makes failures observable during evaluation.

## Controls Already Implemented

- Hybrid RAG over a local corpus.
- Citation objects returned to the client.
- Domain profiles that narrow allowed behavior.
- Minimum grounding thresholds.
- Optional answer verification hooks.
- Abstention-first response patterns for unsupported claims.
- Prompt injection and abuse guardrails.

## Recommended Next Steps

- Add a dedicated reranker for retrieval precision.
- Add sentence-level citation checking.
- Add domain-specific golden sets and regression gates.
- Add a second-pass verifier or local judge model.
- Block factual answers that have no source coverage for the target intent.

## Engineering Rule Of Thumb

If the answer depends on changing facts, the safest default is:

1. retrieve evidence,
2. use a tool if available,
3. abstain if support is still insufficient.
