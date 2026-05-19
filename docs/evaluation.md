# Evaluacion automatica

## Objetivo

La evaluacion del core se centra primero en retrieval y grounding. Antes de evaluar si el modelo redacta bonito, conviene verificar que el sistema recupera las fuentes correctas.

## Golden set

El dataset inicial vive en:

```text
datasets/evaluation/golden_general_es.jsonl
```

Cada linea define:

- `id`: identificador estable.
- `question`: pregunta de prueba.
- `must_retrieve`: terminos que deben aparecer en los chunks recuperados.
- `forbidden_answer_terms`: terminos que no deberian aparecer en una respuesta final.

## Ejecucion

```bash
python scripts/evaluate_golden_set.py
```

Tambien hay endpoint:

```bash
curl -X POST http://127.0.0.1:8000/v1/admin/evaluations/retrieval
```

## Siguiente nivel

- evaluacion con LLM juez local,
- verificacion de citas por frase,
- golden sets por dominio,
- umbrales diferentes para hospital, empresa y ayuntamiento.
