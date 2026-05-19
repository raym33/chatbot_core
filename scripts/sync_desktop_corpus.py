from __future__ import annotations

import shutil
from pathlib import Path


SOURCE_DIR = Path("/Users/mac/Desktop/chatbot")
TARGET_DIR = Path(__file__).resolve().parent.parent / "data" / "corpus"


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for path in sorted(SOURCE_DIR.glob("*.md")):
        target = TARGET_DIR / path.name
        shutil.copy2(path, target)
        copied += 1
    print(f"Copiados {copied} ficheros Markdown a {TARGET_DIR}")


if __name__ == "__main__":
    main()
