# Arquitectura de referencia

## Objetivo

Esta implementacion usa `FastAPI` como gateway conversacional, `LM Studio` como proveedor principal de inferencia local y `Gemma 4 26B A4B Instruct` como modelo de respuesta. El objetivo es que el MacBook actue como punto de entrada y que los Mac mini vayan asumiendo carga de inferencia segun se abra el cluster.

## Componentes

- `app/main.py`: API REST y WebSocket, sesiones, feedback y administracion del corpus.
- `app/chat.py`: politicas conversacionales, deteccion de intencion y generacion con citas.
- `app/rag.py`: recuperacion hibrida lexical + semantica con cache local de embeddings.
- `app/llm.py`: clientes para `LM Studio` y `Ollama`, tanto para chat como para embeddings.
- `app/static/munibot.js`: widget embebible con `Shadow DOM`.

## Flujo de una pregunta

1. El widget crea una sesion.
2. El backend recupera chunks del corpus con puntuacion hibrida.
3. Se construye un prompt con contexto municipal y guardrails basicos.
4. `Gemma 4 26B` responde a traves del servidor OpenAI-compatible de `LM Studio`.
5. El backend devuelve texto, citas y acciones sugeridas.

## RAG actual

- Recuperacion lexical: `TF-IDF` ligero en memoria.
- Recuperacion semantica: embeddings via `LM Studio` con `text-embedding-nomic-embed-text-v1.5`.
- Fusion de scores: `45 % lexical` y `55 % semantico` por defecto.
- Persistencia de embeddings: `data/rag_index.json`.

## Proveedores

### LM Studio

- Chat principal: `gemma-4-26b-a4b-it-mlx`
- Embeddings: `text-embedding-nomic-embed-text-v1.5`
- Endpoint por defecto: `http://127.0.0.1:1234`

### Ollama

- Fallback opcional para entorno distribuido.
- Modelo recomendado: `qwen3.5:9b`

## Estado del proyecto

La base ya es util para piloto interno: conversaciones, citas de fuente, ingestado de corpus y administracion minima. Aun faltan integraciones reales de cita previa, incidencias, autenticacion fuerte y observabilidad avanzada.
