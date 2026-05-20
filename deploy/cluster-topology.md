# Reference Cluster Topology

## Roles

| Node | Example host | Role |
|---|---|---|
| Gateway | `gateway.internal` | FastAPI gateway, widget delivery, persistence, orchestration |
| Worker A | `worker-a.internal` | Primary chat inference |
| Worker B | `worker-b.internal` | Secondary chat inference |
| Worker C | `worker-c.internal` | Heavy reasoning or optional multimodal tasks |

## Suggested Models

| Use case | Model |
|---|---|
| Default chat | `qwen3.5:9b` |
| Heavier reasoning | `qwen3:30b` |
| Embeddings | `bge-m3` |
| Optional vision | `gemma3:12b` |

## Operational Guidance

- Keep at least two homogeneous chat workers for predictable routing.
- Reserve the heaviest model for low-frequency complex requests.
- Prefer stateless workers and centralized persistence at the gateway layer.
- Treat the gateway as an orchestrator, not as the only inference node.
