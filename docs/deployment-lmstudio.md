# Despliegue con LM Studio y Gemma 4 26B

## Requisitos

- `LM Studio.app` instalado en el MacBook.
- Servidor local activo en `127.0.0.1:1234`.
- Modelo `gemma-4-26b-a4b-it-mlx` descargado.
- Embedding `text-embedding-nomic-embed-text-v1.5` descargado.

## Comandos utiles

### Comprobar servidor

```bash
lms server status
curl http://127.0.0.1:1234/v1/models
```

### Cargar Gemma 4

```bash
lms load gemma-4-26b-a4b-it-mlx --identifier munibot-gemma4 --ttl 1800 -y
```

### Arrancar el chatbot

```bash
cp deploy/cluster.example.env .env
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Variables recomendadas

```env
MUNIBOT_AI_BACKEND=lmstudio
MUNIBOT_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
MUNIBOT_LMSTUDIO_CHAT_MODEL=gemma-4-26b-a4b-it-mlx
MUNIBOT_LMSTUDIO_EMBED_MODEL=text-embedding-nomic-embed-text-v1.5
MUNIBOT_ENABLE_SEMANTIC_RAG=true
```

## Integracion futura con los Mac mini

- Mantener `LM Studio` y `Gemma 4` en el MacBook para calidad alta y authoring.
- Usar `Ollama + qwen3.5:9b` en mini1 y mini2 para servir trafico masivo.
- Reservar mini3 para un modelo mayor o para vision.
- Dejar mini4 como canary o respaldo.
