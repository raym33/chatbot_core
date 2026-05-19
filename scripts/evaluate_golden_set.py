from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from app.config import get_settings
from app.evaluation import run_retrieval_evaluation
from app.rag import Retriever


async def main() -> int:
    settings = get_settings()
    golden_path = Path(sys.argv[1]) if len(sys.argv) > 1 else settings.golden_set_path
    retriever = Retriever(settings.corpus_dir, settings.rag_index_path)
    await retriever.load()
    result = await run_retrieval_evaluation(retriever, golden_path, top_k=settings.top_k)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
