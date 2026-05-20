# Chatbot Core
Repositorio base para construir chatbots avanzados multi-dominio: empresa, hospital, ayuntamiento, soporte interno o cualquier organizacion que necesite respuestas con grounding documental, herramientas y control fuerte de alucinaciones.

## Que incluye

- Backend `FastAPI` con sesiones, historial, feedback, escalado y administracion basica del corpus.
- Widget web embebible `<munibot-widget>` con `Shadow DOM`.
- Motor RAG hibrido lexical + semantico sobre ficheros Markdown locales.
- Clientes de inferencia configurables para `LM Studio` y `Ollama`.
- Integracion preparada para `Gemma 4 26B` y embeddings locales con `LM Studio`.
- Perfiles de dominio para ayuntamiento, hospital y empresa.
- Estructura base de fine-tuning supervisado multi-dominio.
- Politicas de abstencion para reducir drásticamente el riesgo de alucinacion.
- Tool calling inicial para citas, incidencias y escalado humano.
- Voz en espanol con `edge-tts` y transcripcion local con `Whisper`.
- Golden set y script de evaluacion automatica de retrieval.
- Controles de seguridad contra prompt injection, abuso de recursos y payloads excesivos.
- Capa inicial de privacidad: redaccion PII, exportacion, supresion, anonimizacion y retencion.
- Packs sectoriales en `skills/` para hospital, ayuntamiento, seguros, legal, finanzas,
  tractores, dental, estetica y taller mecanico.
- Contratos MCP en `mcps/` para CRM, ERP, citas, seguros, HIS, OCR, DMS, ticketing y GIS.

## Filosofia de arquitectura

- `RAG` para conocimiento factual.
- `Fine-tuning` para comportamiento.
- `Tools/API` para datos variables.
- `Abstention first`: si no hay soporte verificable, responder "no puedo confirmarlo".

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

2. Copiar el corpus de ejemplo:

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
| `MUNIBOT_ORGANIZATION_NAME` | Nombre visible de la organizacion |
| `MUNIBOT_ORGANIZATION_TYPE` | `company`, `hospital`, `cityhall`, etc. |
| `MUNIBOT_DOMAIN_PROFILE_PATH` | Perfil JSON del dominio |
| `MUNIBOT_APPOINTMENT_URL` | URL de reserva, cita o agenda |
| `MUNIBOT_HUMAN_HANDOFF_URL` | URL del CRM o soporte humano |
| `MUNIBOT_EDGE_TTS_VOICE` | Voz de `edge-tts`, por ejemplo `es-ES-AlvaroNeural` |
| `MUNIBOT_WHISPER_MODEL_NAME` | Modelo Whisper local para STT, por ejemplo `base` |

## Voz y audio

El widget puede grabar audio del microfono, transcribirlo a texto con `Whisper` y leer respuestas en espanol con `edge-tts`.

Endpoints:

- `POST /v1/audio/transcriptions`
- `POST /v1/audio/speech`

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
- Demo hospitalaria reproducible: `deploy/hospital-demo.env.example`
- Inventario hospitalario de la red `192.168.100.0/24`: `deploy/nodes.hospital-demo.json`

En esta sesion he podido detectar `mini1` y `mini2` en `192.168.100.50` y `192.168.100.51`, pero no he podido entrar porque este MacBook aun no tiene credenciales autorizadas en esos equipos.

## Modelos que recomiendo

### Produccion local

- `gemma-4-26b-a4b-it-mlx` como modelo principal de chat cuando prima la calidad.
- `text-embedding-nomic-embed-text-v1.5` como modelo de embeddings.
- `qwen3.5:9b` cuando quieras throughput distribuido y coste razonable.
- `qwen3:30b` para razonamiento pesado o tool use avanzado.
- `qwen3-embedding:4b` o `bge-m3` si quieres embeddings fuera de `LM Studio`.

### Por que esta combinacion

- `qwen3.5` en Ollama ofrece variantes pequeñas y medianas con ventana de `256K`, y el tag `9b` pesa unos `6.6GB`, razonable para Apple Silicon.
- `qwen3` es muy fuerte en razonamiento y agente, pero `30b` conviene reservarlo para un nodo concreto.
- `Gemma 4 26B` es un buen candidato para respuestas cuidadas y grounding fuerte.

## Fine-tuning

La estructura base esta en:

- `datasets/fine_tuning/`
- `skills/*/fine_tuning_seed.jsonl`
- `scripts/build_finetune_seed_dataset.py`
- `scripts/validate_finetune_dataset.py`
- `docs/fine_tuning.md`

La recomendacion es hacer fine-tuning solo para comportamiento, no para memorizar la documentacion viva.

## Packs sectoriales

La arquitectura separa `core comun + packs sectoriales`:

- `app/`: logica comun, RAG, seguridad, privacidad, herramientas base.
- `skills/`: reglas sectoriales, intents, abstenciones, golden sets y semillas de fine-tuning.
- `mcps/`: contratos de integracion para datos vivos y acciones reales.
- `docs/playbooks/sector-packs.md`: guia para crear y validar nuevos packs.

Packs iniciales:

- `hospital`
- `medium_cityhall`
- `insurance_agency`
- `legal_office`
- `financial_advisor`
- `tractor_sales`
- `dental_clinic`
- `aesthetic_clinic`
- `mechanic_workshop`

## Scripts utiles

- `python scripts/sync_desktop_corpus.py`
- `python scripts/check_ollama_nodes.py`
- `bash scripts/run_gateway.sh`
- `bash scripts/run_ollama_node.sh`
- `bash scripts/distribute_project.sh usuario 192.168.1.21 192.168.1.22`
- `bash scripts/generate_ssh_key.sh`
- `bash scripts/bootstrap_ollama_node.sh`
- `python scripts/deploy_cluster.py`
- `python scripts/build_finetune_seed_dataset.py`
- `python scripts/validate_finetune_dataset.py datasets/fine_tuning/seed_general_es.jsonl`
- `python scripts/evaluate_golden_set.py`
- `python scripts/validate_sector_packs.py`

## Documentacion adicional

- `docs/architecture.md`
- `docs/deployment-lmstudio.md`
- `docs/models.md`
- `docs/fine_tuning.md`
- `docs/hallucination-control.md`
- `docs/evaluation.md`
- `docs/tool-calling.md`
- `docs/anti-hallucination-playbook.md`
- `docs/security-and-abuse.md`
- `docs/frameworks-and-runtime.md`
- `docs/capacity-planning.md`
- `docs/multimodal-annex.md`
- `docs/references.md`
- `docs/privacy-rgpd-ens.md`
- `docs/playbooks/sector-packs.md`

## Sobre "alucinaciones 0"

No se puede garantizar `0` alucinaciones en sentido absoluto con un LLM generativo. Lo que si se puede hacer, y este repo persigue, es:

- grounding documental,
- abstencion por defecto cuando falta soporte,
- perfiles por dominio,
- evaluacion continua,
- herramientas en tiempo real,
- escalado humano en casos sensibles.

## Licencia

Este proyecto se publica bajo licencia MIT. Consulte `LICENSE`.
