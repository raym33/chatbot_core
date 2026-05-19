from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MCPS_DIR = ROOT / "mcps"

REQUIRED_PACK_FILES = {
    "README.md",
    "SKILL.md",
    "profile.json",
    "intents.json",
    "tools.json",
    "golden_set.jsonl",
    "fine_tuning_seed.jsonl",
}

EXPECTED_PACKS = {
    "aesthetic_clinic",
    "dental_clinic",
    "financial_advisor",
    "hospital",
    "insurance_agency",
    "legal_office",
    "mechanic_workshop",
    "medium_cityhall",
    "tractor_sales",
}


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} debe contener un objeto JSON")
    return payload


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number} debe contener un objeto JSON")
        rows.append(payload)
    if not rows:
        raise ValueError(f"{path} no puede estar vacio")
    return rows


def _validate_skill_frontmatter(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.startswith("---\n"):
        errors.append(f"{path}: falta frontmatter YAML")
    if "name:" not in text.split("---", maxsplit=2)[1]:
        errors.append(f"{path}: falta name en frontmatter")
    if "description:" not in text.split("---", maxsplit=2)[1]:
        errors.append(f"{path}: falta description en frontmatter")
    return errors


def validate_pack(pack_dir: Path) -> list[str]:
    errors: list[str] = []
    existing = {path.name for path in pack_dir.iterdir() if path.is_file()}
    missing = REQUIRED_PACK_FILES - existing
    if missing:
        errors.append(f"{pack_dir}: faltan archivos {sorted(missing)}")
        return errors

    try:
        profile = _load_json(pack_dir / "profile.json")
        if not profile.get("organization_type"):
            errors.append(f"{pack_dir}/profile.json: falta organization_type")
        if not profile.get("response_rules"):
            errors.append(f"{pack_dir}/profile.json: falta response_rules")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{pack_dir}/profile.json: {exc}")

    try:
        intents = _load_json(pack_dir / "intents.json")
        if not intents.get("intents"):
            errors.append(f"{pack_dir}/intents.json: falta intents")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{pack_dir}/intents.json: {exc}")

    try:
        tools = _load_json(pack_dir / "tools.json")
        for tool in tools.get("tools", []):
            target = tool.get("mcp_target")
            if target and not (ROOT / target / "manifest.json").exists():
                errors.append(f"{pack_dir}/tools.json: MCP no encontrado {target}")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{pack_dir}/tools.json: {exc}")

    try:
        _load_jsonl(pack_dir / "golden_set.jsonl")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{pack_dir}/golden_set.jsonl: {exc}")

    try:
        seeds = _load_jsonl(pack_dir / "fine_tuning_seed.jsonl")
        for row in seeds:
            messages = row.get("messages")
            if not isinstance(messages, list) or len(messages) < 2:
                errors.append(f"{pack_dir}/fine_tuning_seed.jsonl: messages invalido")
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{pack_dir}/fine_tuning_seed.jsonl: {exc}")

    errors.extend(_validate_skill_frontmatter(pack_dir / "SKILL.md"))
    return errors


def main() -> int:
    errors: list[str] = []
    pack_names = {
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    missing_packs = EXPECTED_PACKS - pack_names
    if missing_packs:
        errors.append(f"Faltan packs esperados: {sorted(missing_packs)}")

    for pack_name in sorted(EXPECTED_PACKS & pack_names):
        errors.extend(validate_pack(SKILLS_DIR / pack_name))

    for manifest_path in sorted(MCPS_DIR.glob("*/manifest.json")):
        try:
            manifest = _load_json(manifest_path)
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{manifest_path}: {exc}")
            continue
        if not manifest.get("tools"):
            errors.append(f"{manifest_path}: falta tools")
        if not manifest.get("data_classification"):
            errors.append(f"{manifest_path}: falta data_classification")

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Packs sectoriales validos: {len(EXPECTED_PACKS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
