# Sector Skill Packs

Los `skills/` son packs sectoriales reutilizables para adaptar `chatbot_core` a una vertical concreta sin convertir el core en un chatbot monolitico.

Cada pack incluye:

- `profile.json`: configuracion ligera de dominio.
- `SKILL.md`: reglas operativas, limites y workflow sectorial.
- `intents.json`: intenciones soportadas, ejemplos y riesgo.
- `tools.json`: herramientas esperadas y MCP asociado.
- `golden_set.jsonl`: evaluacion minima anti-alucinacion.
- `fine_tuning_seed.jsonl`: semillas para ajustar comportamiento, no conocimiento factual vivo.
- `README.md`: guia de uso del pack.

## Packs iniciales

| Pack | Riesgo | Uso principal |
|---|---:|---|
| `hospital` | Alto | Admision, citas, informacion administrativa sanitaria |
| `medium_cityhall` | Medio | Tramites, padron, licencias, incidencias, cita previa |
| `insurance_agency` | Medio/alto | Polizas, siniestros, citas con agente |
| `legal_office` | Alto | Intake, citas, documentacion, derivacion a abogado |
| `financial_advisor` | Alto | Educacion financiera y derivacion regulada |
| `tractor_sales` | Medio | Catalogo, ofertas, recambios, taller |
| `dental_clinic` | Medio | Citas, tratamientos generales, urgencias dentales |
| `aesthetic_clinic` | Medio | Tratamientos, valoraciones, consentimientos |
| `mechanic_workshop` | Medio | Citas, reparaciones, recambios, seguridad vial |

## Como usar un pack

1. Copiar `skills/<pack>/profile.json` o apuntar `MUNIBOT_DOMAIN_PROFILE_PATH` a ese archivo.
2. Ingerir documentacion fija del cliente en `data/corpus/`.
3. Implementar los MCP de `tools.json` que necesiten datos vivos.
4. Ejecutar golden sets del pack antes de produccion.
5. Ajustar fine-tuning solo para tono, abstencion y workflow.
