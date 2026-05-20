from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "deploy" / "nodes.example.json"
KEY_PATH = Path.home() / ".ssh" / "chatbot_core_cluster_ed25519"
REMOTE_DIR = "~/chatbot_core"


def run(cmd: list[str]) -> None:
    print("+", " ".join(shlex.quote(part) for part in cmd))
    subprocess.run(cmd, check=True)


def ssh_cmd(user: str, host: str, remote: str) -> list[str]:
    return [
        "ssh",
        "-i",
        str(KEY_PATH),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        f"{user}@{host}",
        remote,
    ]


def rsync_cmd(user: str, host: str) -> list[str]:
    return [
        "rsync",
        "-az",
        "--delete",
        "-e",
        f"ssh -i {KEY_PATH} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
        "--exclude",
        ".venv",
        "--exclude",
        "__pycache__",
        "--exclude",
        ".pytest_cache",
        "--exclude",
        ".ruff_cache",
        str(ROOT) + "/",
        f"{user}@{host}:{REMOTE_DIR}/",
    ]


def main() -> None:
    if not INVENTORY.exists():
        raise SystemExit(f"Inventory file not found: {INVENTORY}")
    if not KEY_PATH.exists():
        raise SystemExit(
            f"SSH key not found at {KEY_PATH}. Run scripts/generate_ssh_key.sh first."
        )

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    workers = inventory.get("workers", [])

    for worker in workers:
        user = worker["user"]
        host = worker["host"]
        models = " ".join(worker.get("models", []))

        run(rsync_cmd(user, host))
        run(
            ssh_cmd(
                user,
                host,
                (
                    "mkdir -p ~/chatbot_core && "
                    "cd ~/chatbot_core && "
                    "chmod +x scripts/*.sh && "
                    f"MODEL_LIST={shlex.quote(models)} bash scripts/bootstrap_ollama_node.sh"
                ),
            )
        )

    print("Remote deployment completed.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
