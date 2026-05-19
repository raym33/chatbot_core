# Playbook anti-alucinaciones

## Principio base

La meta operativa no es prometer alucinaciones cero, sino hacer que el sistema:

- responda solo con soporte documental o de herramientas,
- cite fuentes,
- se abstenga cuando falte soporte,
- escale casos sensibles,
- mida fallos con evaluacion continua.

## Tecnicas listas por capa

| Capa | Tecnica | Para que sirve | Estado en repo |
|---|---|---|---|
| Ingesta | Normalizacion y versionado del corpus | Evita fuentes duplicadas, obsoletas o contradictorias | Base Markdown |
| Retrieval | RAG hibrido lexical + semantico | Recupera por palabras exactas y significado | Implementado |
| Retrieval | Reranking | Reordena evidencias antes de generar | Pendiente |
| Respuesta | Citas obligatorias | Hace auditable la respuesta | Implementado |
| Respuesta | Abstencion por falta de soporte | Evita inventar cuando no hay fuente | Implementado |
| Verificacion | Grounding verifier | Mide si la respuesta esta apoyada por citas/herramientas | Implementado |
| Seguridad | Prompt injection guard | Bloquea intentos de cambiar reglas internas | Implementado |
| Seguridad | Rate limiting | Reduce abuso y agotamiento de recursos | Implementado |
| Evaluacion | Golden set | Comprueba retrieval minimo antes de release | Implementado |
| Evaluacion | LLM-as-judge local | Evalua factualidad y tono con otro modelo | Pendiente |
| Operacion | Human handoff | Deriva casos de riesgo o baja confianza | Implementado como stub |

## Politica recomendada por dominio

| Dominio | Umbral | Regla |
|---|---:|---|
| Hospital | Muy alto | Abstenerse ante sintomas, diagnosticos, prescripciones o urgencias |
| Ayuntamiento | Alto | Abstenerse si no hay fuente para plazos, requisitos, importes o decisiones |
| Empresa | Medio/alto | Abstenerse en contratos, precios, compromisos y seguridad |
| Soporte interno | Medio | Responder con KB o herramienta; si no, abrir ticket |

## Regla de oro

El modelo no debe ser la base de datos. El modelo redacta; el RAG y las herramientas prueban.
