from app.models import Citation
from app.verifier import GroundingVerifier


def test_verifier_accepts_grounded_answer() -> None:
    verifier = GroundingVerifier(min_grounding_score=0.1)
    result = verifier.verify(
        answer="La cita previa se gestiona por canales oficiales.",
        citations=[
            Citation(
                source="FAQ",
                path="faq.md",
                snippet="La cita previa se gestiona mediante canales oficiales.",
            )
        ],
        tool_results=[],
    )

    assert result.grounded


def test_verifier_rejects_unsupported_answer() -> None:
    verifier = GroundingVerifier(min_grounding_score=0.5)
    result = verifier.verify(
        answer="El tramite esta garantizado para manana con coste cero.",
        citations=[Citation(source="FAQ", path="faq.md", snippet="La cita previa existe.")],
        tool_results=[],
    )

    assert not result.grounded
