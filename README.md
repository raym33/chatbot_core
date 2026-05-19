# Munibot Local

Implementacion del chatbot municipal de la carpeta `/Users/mac/Desktop/chatbot`, aterrizada para ejecutarse en una red local de `5` Macs conectados por Ethernet y orientada a `LM Studio + Gemma 4 26B` como backend principal local.

## Que incluye

- Backend `FastAPI` con sesiones, historial, feedback, escalado y administracion basica del corpus.
- Widget web embebible `<munibot-widget>` con `Shadow DOM`.
- Motor RAG hibrido lexical + semantico sobre ficheros Markdown locales.
- Clientes de inferencia configurables para `LM Studio` y `Ollama`.
- Integracion preparada para `Gemma 4 26B` y embeddings locales con `LM Studio`.
- Scripts para copiar el corpus desde `/Users/mac/Desktop/chatbot` y preparar el despliegue en tus Macs.

## Topologia recomendada para tus 5 Macs

| Equipo | Rol recomendado |
|---|---|
| MacBook | API Gateway, widget web, base SQLite, observabilidad basica |
| Mac mini 1 | Nodo `Ollama` principal |
| Mac mini 2 | Nodo `Ollama` secundario |
| Mac mini 3 | Nodo `Ollama` para embeddings o modelo alternativo |
| Mac mini 4 | Nodo de respaldo, pruebas y futuras integraciones |

La app funciona sin GPU NVIDIA. La idea es aprovechar Apple Silicon con `LM Studio` para el modelo principal y `Ollama` cuando quieras repartir trafico entre los minis.

## Arranque rapido en este Mac

1. Crear entorno e instalar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2. Copiar el corpus municipal de ejemplo:

```bash
python scripts/sync_desktop_corpus.py
```

3. Definir los nodos `Ollama` que quieras usar:

```bash
cp deploy/cluster.example.env .env
```

4. Arrancar el backend:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Abrir la demo:

- `http://localhost:8000/static/demo.html`

## Variables importantes

| Variable | Uso |
|---|---|
| `MUNIBOT_AI_BACKEND` | `lmstudio` u `ollama` |
| `MUNIBOT_LMSTUDIO_BASE_URL` | URL del servidor local de LM Studio |
| `MUNIBOT_LMSTUDIO_CHAT_MODEL` | Modelo principal de chat en LM Studio |
| `MUNIBOT_LMSTUDIO_EMBED_MODEL` | Modelo de embeddings en LM Studio |
| `MUNIBOT_OLLAMA_HOSTS_RAW` | Lista separada por comas de nodos `Ollama`, por ejemplo `http://192.168.1.21:11434,http://192.168.1.22:11434` |
| `MUNIBOT_CORPUS_DIR` | Carpeta del corpus Markdown |
| `MUNIBOT_CITY_NAME` | Nombre visible del ayuntamiento |
| `MUNIBOT_APPOINTMENT_URL` | URL del sistema de cita previa |
| `MUNIBOT_HUMAN_HANDOFF_URL` | URL del formulario o CRM de escalado humano |

## Despliegue distribuido en los 5 Macs

1. En cada Mac mini instala `Ollama`.
2. Arranca `Ollama` escuchando en la LAN:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

3. Descarga el modelo en cada nodo:

```bash
ollama pull qwen2.5:7b-instruct
```

4. En el MacBook pon en `.env` las IPs Ethernet de los minis.
5. Ejecuta la API en el MacBook y expone `8000` en la red local.

### Automatizacion del cluster

He dejado preparados estos artefactos:

- Inventario de ejemplo: `deploy/nodes.example.json`
- Topologia y reparto de roles: `deploy/cluster-topology.md`
- Plantilla `launchd` para `Ollama`: `deploy/com.munibot.ollama.plist.template`
- Generacion de clave: `bash scripts/generate_ssh_key.sh`
- Bootstrap local de un nodo: `bash scripts/bootstrap_ollama_node.sh`
- Despliegue remoto por `SSH`: `python scripts/deploy_cluster.py`

En esta sesion he podido detectar `mini1` y `mini2` en `192.168.100.50` y `192.168.100.51`, pero no he podido entrar porque este MacBook aun no tiene credenciales autorizadas en esos equipos.

## Modelos que recomiendo para tus Macs

### Produccion local

- `gemma-4-26b-a4b-it-mlx` como modelo principal de chat en el MacBook con `LM Studio`.
- `text-embedding-nomic-embed-text-v1.5` como modelo de embeddings.
- `qwen3.5:9b` en los minis cuando quieras throughput distribuido.
- `qwen3:30b` solo en un mini dedicado para consultas mas complejas.
- `qwen3-embedding:4b` o `bge-m3` si en el cluster final quieres embeddings fuera de `LM Studio`.

### Por que esta combinacion

- `qwen3.5` en Ollama ofrece variantes pequeñas y medianas con ventana de `256K`, y el tag `9b` pesa unos `6.6GB`, razonable para Apple Silicon.
- `qwen3` es muy fuerte en razonamiento y agente, pero `30b` conviene reservarlo para un nodo concreto.
- `Gemma 4 26B` ya esta instalado en `LM Studio` en este Mac y es un muy buen candidato para redaccion institucional y piloto local.

## Scripts utiles

- `python scripts/sync_desktop_corpus.py`
- `python scripts/check_ollama_nodes.py`
- `bash scripts/run_gateway.sh`
- `bash scripts/run_ollama_node.sh`
- `bash scripts/distribute_project.sh usuario 192.168.1.21 192.168.1.22`
- `bash scripts/generate_ssh_key.sh`
- `bash scripts/bootstrap_ollama_node.sh`
- `python scripts/deploy_cluster.py`

## Documentacion adicional

- `docs/architecture.md`
- `docs/deployment-lmstudio.md`
- `docs/models.md`

## Limitaciones actuales

- El RAG del MVP usa recuperacion lexical y citas; no incluye Milvus ni OpenSearch.
- Las integraciones de cita e incidencias estan preparadas como stubs configurables.
- La persistencia es `SQLite` para ir rapido en laboratorio; luego se puede pasar a `PostgreSQL`.
