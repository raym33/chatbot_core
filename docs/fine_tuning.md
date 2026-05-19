# Estructura general de fine-tuning

## Objetivo

El repo incluye una base de fine-tuning pensada para cualquier sector: empresa, hospital, ayuntamiento o servicio interno.

## Recomendacion

Separar tres capas:

1. `RAG` para conocimiento factual y citable.
2. `Fine-tuning` para comportamiento.
3. `Herramientas/API` para datos vivos.

## Que entrenar

- tono,
- formatos de respuesta,
- lectura facil,
- abstencion,
- clasificacion de intenciones,
- escalado a humano,
- estructura de respuestas con citas.

## Que no entrenar como memoria principal

- normativa cambiante,
- precios,
- horarios vivos,
- citas,
- estados de procesos,
- informacion clinica o legal que exija trazabilidad documental.

## Artefactos incluidos

- perfiles de dominio en `profiles/`
- dataset semilla en `datasets/fine_tuning/`
- validador de dataset en `scripts/validate_finetune_dataset.py`
- generador de dataset semilla en `scripts/build_finetune_seed_dataset.py`
