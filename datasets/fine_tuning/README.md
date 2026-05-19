# Fine-tuning

Esta carpeta contiene la estructura base para fine-tuning supervisado.

## Objetivo recomendado

Usar fine-tuning para:

- tono y estilo de respuesta,
- politicas de abstencion,
- clasificacion de intenciones,
- formatos de salida,
- escalado a humano.

No usarlo como sustituto del RAG para datos factuales que cambian.

## Archivos

- `seed_general_es.jsonl`: dataset semilla multi-dominio en español.

## Formato

Cada linea del JSONL debe tener esta forma:

```json
{
  "messages": [
    {"role": "system", "content": "Instrucciones"},
    {"role": "user", "content": "Pregunta"},
    {"role": "assistant", "content": "Respuesta objetivo"}
  ]
}
```

## Validacion

```bash
python scripts/validate_finetune_dataset.py datasets/fine_tuning/seed_general_es.jsonl
```
