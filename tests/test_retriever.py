from pathlib import Path

from app.rag import Retriever


def test_retriever_finds_cita_content(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "faq.md").write_text(
        "# Cita previa\n\nLa cita previa municipal se gestiona mediante canales oficiales.\n",
        encoding="utf-8",
    )

    retriever = Retriever(corpus, tmp_path / "index.json")

    import asyncio

    asyncio.run(retriever.load())
    results = asyncio.run(retriever.search("quiero pedir cita previa", top_k=1))

    assert results
    assert "cita" in results[0].text.lower()
