# Hospital Pack

Pack sectorial para hospitales, clinicas grandes y servicios asistenciales.

## Objetivo

Atender dudas administrativas y operativas sin diagnosticar, prescribir ni sustituir al personal sanitario.

## Contenido

- `profile.json`: configuracion de tono, riesgos y reglas.
- `SKILL.md`: instrucciones operativas del sector.
- `intents.json`: intents soportados y criterios de escalado.
- `tools.json`: herramientas esperadas e integraciones MCP.
- `golden_set.jsonl`: casos de evaluacion con respuestas esperadas.
- `fine_tuning_seed.jsonl`: ejemplos semilla para comportamiento.

## Regla principal

Si la consulta tiene sintomas, urgencia, diagnostico, medicacion, resultados clinicos o tratamiento, el chatbot debe abstenerse de resolver y derivar a profesionales sanitarios o emergencias.

## Estado en el core

Este pack ya tiene una vertical de referencia conectada en el core para:

- disponibilidad de citas,
- reserva demostrativa de cita,
- estado de admision,
- escalado humano,
- OCR documental administrativo.
