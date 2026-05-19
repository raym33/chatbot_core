from __future__ import annotations

import os
from urllib.error import URLError
from urllib.request import urlopen


def main() -> None:
    raw = os.environ.get("MUNIBOT_OLLAMA_HOSTS_RAW", "http://127.0.0.1:11434")
    hosts = [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]
    for host in hosts:
        url = f"{host}/api/tags"
        try:
            with urlopen(url, timeout=4) as response:
                status = response.status
            print(f"[OK] {host} -> {status}")
        except URLError as exc:
            print(f"[ERROR] {host} -> {exc}")


if __name__ == "__main__":
    main()
