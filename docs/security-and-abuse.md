# Seguridad, abuso y prompt injection

## Amenazas cubiertas

| Amenaza | Riesgo | Mitigacion en este repo |
|---|---|---|
| Prompt injection | Cambiar reglas internas o revelar prompts | `InputGuard` en `app/security.py` |
| System prompt leakage | Filtracion de instrucciones internas | Bloqueo por patrones + no incluir secretos en prompts |
| Unbounded consumption | Coste alto o caida por abuso | Rate limiting HTTP + limites de payload |
| Preguntas fuera de dominio | Ruido, riesgo reputacional y consumo inutil | `strict_domain_guard` opcional |
| Tool abuse | Llamadas excesivas o peligrosas | Registro de herramientas y stubs controlados |
| RAG poisoning | Fuentes maliciosas o obsoletas | Versionado, evaluacion y futura firma de documentos |
| DoS de WebSocket | Mensajes enormes o bucles | Limite de tamano por mensaje |

## Controles de configuracion

| Variable | Valor por defecto | Uso |
|---|---:|---|
| `MUNIBOT_MAX_MESSAGE_CHARS` | `4000` | Limite de caracteres por mensaje |
| `MUNIBOT_REQUEST_BODY_LIMIT_BYTES` | `64000` | Limite de cuerpo HTTP |
| `MUNIBOT_REQUESTS_PER_MINUTE` | `90` | Rate limit por IP |
| `MUNIBOT_STRICT_DOMAIN_GUARD` | `false` | Bloqueo estricto de consultas fuera de dominio |
| `MUNIBOT_ENABLE_ANSWER_VERIFICATION` | `true` | Verificacion de grounding |

## Recomendacion productiva

En produccion, el rate limiter en memoria debe moverse a una capa compartida:

- Kong, Traefik, Envoy o NGINX para edge.
- Redis para contador distribuido.
- WAF con reglas especificas de LLM.
- Cola por sesion para limitar concurrencia por usuario.

## Mapeo OWASP LLM Top 10

| OWASP | Control |
|---|---|
| LLM01 Prompt Injection | `InputGuard`, prompts con separacion de contexto, tool allowlist |
| LLM02 Sensitive Information Disclosure | no incluir secretos, redaccion de PII pendiente |
| LLM05 Improper Output Handling | salida estructurada y verificacion |
| LLM06 Excessive Agency | herramientas allowlist y sin acciones irreversibles automaticas |
| LLM07 System Prompt Leakage | bloqueo de exfiltracion e instrucciones internas fuera del prompt visible |
| LLM08 Vector and Embedding Weaknesses | evaluacion de retrieval y versionado de corpus |
| LLM09 Misinformation | RAG, citas, abstencion y golden sets |
| LLM10 Unbounded Consumption | rate limits, limites de payload y TTL de modelos |
