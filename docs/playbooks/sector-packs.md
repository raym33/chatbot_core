# Sector Packs Playbook

Este playbook explica como crear, adaptar y validar packs sectoriales para `chatbot_core`.

## Arquitectura

```text
chatbot_core/
  app/                 # core comun
  profiles/            # perfiles ligeros globales
  skills/              # packs sectoriales
  mcps/                # contratos de integracion
  datasets/            # evaluacion y fine-tuning general
  docs/playbooks/      # guias de implantacion
```

## Regla de separacion

| Capa | Contiene | No debe contener |
|---|---|---|
| `app/` | Logica comun, RAG, seguridad, privacidad, herramientas base | Reglas sectoriales duras |
| `skills/` | Reglas, tono, abstencion, intents, golden tests | Credenciales, datos vivos |
| `mcps/` | Contratos de herramientas y datos variables | Prompts, datos personales reales |
| `data/corpus/` | Documentacion fija del cliente | Estados de expediente, stock, agenda |
| `datasets/` | Evaluacion y semillas de comportamiento | Secretos o datos personales reales |

## Como crear un nuevo pack

1. Crear `skills/<sector>/`.
2. Incluir `profile.json`, `SKILL.md`, `intents.json`, `tools.json`, `golden_set.jsonl`,
   `fine_tuning_seed.jsonl` y `README.md`.
3. Clasificar riesgos: bajo, medio, alto o critico.
4. Definir abstenciones obligatorias antes de ejemplos positivos.
5. Mapear datos vivos a `mcps/`, no a RAG.
6. Crear golden tests para fallos peligrosos, no solo para preguntas faciles.
7. Ejecutar `python scripts/validate_sector_packs.py`.

## Patrón de respuesta segura

Para sectores regulados o de alto impacto:

1. Reconocer la necesidad del usuario.
2. Declarar el limite del asistente si aplica.
3. Responder solo con fuente, herramienta o informacion general.
4. Derivar a humano cuando falte soporte o haya riesgo.
5. Evitar recopilar datos personales innecesarios.

## Datos fijos y datos variables

| Tipo | Ejemplos | Canal recomendado |
|---|---|---|
| Fijo | horarios, politicas, requisitos, guias, FAQ | `data/corpus/` + RAG |
| Variable | agenda, stock, expediente, poliza, precio, cita | MCP/tool |
| Sensible | salud, finanzas, legal, menores, expedientes | MCP autenticado + minimizacion |
| Comportamiento | tono, abstencion, flujo, disclaimers | `SKILL.md` + fine-tuning |

## Criterios de salida a produccion

- El pack pasa validacion estructural.
- El golden set pasa con umbral acordado.
- Los MCP devuelven datos estructurados y auditables.
- Existe revision de privacidad/RGPD si hay datos personales.
- Existen limites de tasa, cuotas, timeouts y circuito de handoff humano.
