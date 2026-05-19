from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_MESSAGE_KEYS = {"role", "content"}
VALID_ROLES = {"system", "user", "assistant"}


def validate_line(index: int, payload: dict) -> list[str]:
    errors: list[str] = []
    if "messages" not in payload or not isinstance(payload["messages"], list):
        return [f"linea {index}: falta 'messages' o no es lista"]

    if len(payload["messages"]) < 2:
        errors.append(f"linea {index}: se esperan al menos 2 mensajes")

    for message in payload["messages"]:
        if not REQUIRED_MESSAGE_KEYS.issubset(message):
            errors.append(f"linea {index}: mensaje sin claves requeridas")
            continue
        if message["role"] not in VALID_ROLES:
            errors.append(f"linea {index}: role invalido {message['role']}")
        if not isinstance(message["content"], str) or not message["content"].strip():
            errors.append(f"linea {index}: content vacio")
    return errors


def main(path: str) -> int:
    file_path = Path(path)
    if not file_path.exists():
        print(f"No existe {file_path}")
        return 1

    errors: list[str] = []
    for idx, raw in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"linea {idx}: JSON invalido ({exc})")
            continue
        errors.extend(validate_line(idx, payload))

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Dataset valido: {file_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/validate_finetune_dataset.py <dataset.jsonl>")
    raise SystemExit(main(sys.argv[1]))
