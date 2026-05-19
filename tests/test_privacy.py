from app.privacy import PrivacyProcessor


def test_privacy_processor_redacts_common_pii() -> None:
    processor = PrivacyProcessor(redact_pii=True)
    report = processor.process(
        "Mi DNI es 12345678Z, email ana@example.com, telefono 612345678 e IBAN ES9121000418450200051332"
    )

    assert "12345678Z" not in report.redacted_text
    assert "ana@example.com" not in report.redacted_text
    assert "612345678" not in report.redacted_text
    assert "ES9121000418450200051332" not in report.redacted_text
    assert {"dni_nie", "email", "phone", "iban"}.issubset(set(report.detected_types))


def test_privacy_processor_can_detect_without_redacting() -> None:
    processor = PrivacyProcessor(redact_pii=False)
    report = processor.process("Contacto: test@example.com")

    assert report.redacted_text == "Contacto: test@example.com"
    assert report.detected_types == ["email"]
