import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_sector_packs.py"
spec = importlib.util.spec_from_file_location("validate_sector_packs", VALIDATOR_PATH)
assert spec is not None
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

EXPECTED_PACKS = validator.EXPECTED_PACKS
SKILLS_DIR = validator.SKILLS_DIR
validate_pack = validator.validate_pack


def test_expected_sector_packs_are_complete() -> None:
    for pack_name in EXPECTED_PACKS:
        pack_dir = SKILLS_DIR / pack_name

        assert pack_dir.exists(), f"Falta el pack {pack_name}"
        assert validate_pack(pack_dir) == []


def test_mcp_manifests_exist_for_tool_targets() -> None:
    for pack_name in EXPECTED_PACKS:
        tools_file = SKILLS_DIR / pack_name / "tools.json"
        assert tools_file.exists()

    manifest_paths = list((ROOT / "mcps").glob("*/manifest.json"))
    assert manifest_paths
