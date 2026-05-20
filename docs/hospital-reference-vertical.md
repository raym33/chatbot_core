# Hospital Reference Vertical

This repository includes a reference hospital vertical that is functional without external systems.

It is not meant to replace real HIS, CRM, or appointment infrastructure. It exists to demonstrate how the core can be wired into sector-specific connectors with safe defaults.

## What Is Implemented

- `appointment.availability`
  Returns real demo slots from a local reference connector.
- `appointment.create`
  Creates a demo reservation and persists it locally.
- `hospital.admission_status`
  Returns admission desk, hours, and required documents.
- `handoff.create`
  Queues a demo human handoff ticket.
- `document_ocr.extract`
  Extracts text from allowed local documents and stores a redacted output.

## Local Data

The reference hospital connector stores its seed and runtime files under:

```text
data/demo_backend/hospital/
```

This includes:

- appointment slot catalog,
- admission metadata,
- sample documents,
- runtime appointment reservations,
- runtime handoff tickets.

## Example Tool Calls

### Appointment availability

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "appointment.availability",
    "arguments": {
      "service": "dermatology"
    }
  }'
```

### Appointment creation

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "appointment.create",
    "arguments": {
      "service": "dermatology",
      "slot_id": "DERM-1",
      "contact_ref": "demo-patient"
    }
  }'
```

### Admission status

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "hospital.admission_status",
    "arguments": {
      "area": "general"
    }
  }'
```

### Document intake

```bash
curl -X POST http://127.0.0.1:8000/v1/document-intake \
  -F document=@./data/demo_backend/hospital/documents/admission_authorization.txt
```

### OCR extraction

Use the returned `document_ref` from the intake endpoint:

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "document_ocr.extract",
    "arguments": {
      "document_ref": "returned-file-reference.txt",
      "purpose": "admission_review"
    }
  }'
```

### Human handoff

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "handoff.create",
    "arguments": {
      "queue": "admission",
      "reason": "Patient requests human assistance for admission documents"
    }
  }'
```

## Why This Vertical Matters

This reference implementation shows how the project handles:

- RAG for static knowledge,
- connectors for volatile operational data,
- sector-specific guardrails,
- privacy-aware document processing,
- deterministic evaluation and local reproducibility.
