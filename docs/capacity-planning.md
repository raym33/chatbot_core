# Planificacion de capacidad

## Supuestos de dimensionamiento

Estas cifras son bandas iniciales para planificar. Cada despliegue debe benchmarkearse con su corpus, longitud de contexto, modelo, cuantizacion, politica de streaming y SLA.

Supuesto por mensaje:

- entrada media: `1.200 tokens`
- salida media: `280 tokens`
- trafico pico: `4,8 mensajes/usuario activo/mes`
- margen de seguridad: `40 %`
- objetivo: respuesta media por debajo de `6-10 s`

## Demanda estimada por poblacion

| Poblacion cubierta | Mensajes/mes esperados | Pico msg/s orientativo | Pico con margen 40 % |
|---:|---:|---:|---:|
| 1M | 4,8M | 22 | 31 |
| 2M | 9,6M | 44 | 62 |
| 3M | 14,4M | 66 | 93 |
| 5M | 24,0M | 110 | 154 |

## Hardware y modelos orientativos

| Perfil | Stack | Modelo recomendado | Req/s orientativo | Concurrentes orientativos | Encaje |
|---|---|---|---:|---:|---|
| 1 MacBook/Mac Studio | LM Studio / MLX-LM | Gemma 4 26B, Qwen 27B 4-bit | 0,2-1 | 10-40 | Desarrollo, demo, backoffice |
| 4 Mac mini | Ollama / MLX-LM | Qwen 9B/14B, Gemma 12B | 1-4 | 40-160 | Piloto local, baja carga |
| 1 servidor L40S x4 | vLLM | 8B-14B cuantizado | 15-45 | 500-1.500 | Produccion regional |
| 1 servidor H100 x8 | vLLM/SGLang | 32B-70B FP8/INT4 | 60-160 | 2.000-7.000 | 1M-3M con HA |
| 2 servidores H100/H200 x8 | vLLM/SGLang | 70B + reranker + guard | 120-320 | 5.000-14.000 | 3M-5M con HA |
| Cluster B200/GB200 | vLLM/TensorRT-LLM | 70B-120B o MoE | 300+ | 15.000+ | Gran escala multi-zona |

## Lectura de la tabla

`Req/s` no equivale a usuarios totales. Un chatbot puede atender millones de habitantes con decenas o cientos de req/s si el trafico esta distribuido. Lo que manda es el pico real, la longitud del contexto y el porcentaje de consultas que llegan al LLM tras cache, RAG y herramientas.

## Arquitecturas por escala

| Escala | Arquitectura |
|---|---|
| 2M personas | 2 zonas, 2-4 nodos GPU medianos, Redis, PostgreSQL, object storage, WAF |
| 3M personas | 2 zonas activas, 4-8 nodos GPU, vLLM, cola por sesion, observabilidad completa |
| 5M personas | Multi-zona, GSLB, 8+ nodos GPU, canary de modelos, evaluacion continua, DRP |

## Controles de coste

- cache de respuestas FAQ,
- cache de embeddings,
- top-k bajo y reranker,
- limite de tokens por respuesta,
- streaming con cancelacion,
- cola por usuario,
- degradacion elegante a respuestas extractivas.
