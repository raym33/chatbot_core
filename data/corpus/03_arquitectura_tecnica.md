# 3. ARQUITECTURA TÉCNICA

## 3.1 Visión arquitectónica

La solución se construye sobre un patrón **RAG (Retrieval-Augmented Generation) agéntico**, que combina un modelo de lenguaje generativo con una base de conocimiento municipal estructurada y vectorizada. El sistema se compone de **siete capas** desacopladas, todas desplegadas en infraestructura local, comunicadas mediante APIs internas con autenticación mTLS y cifrado TLS 1.3.

```
┌────────────────────────────────────────────────────────────────────┐
│  CAPA 1 — CANALES                                                  │
│  Web widget (JS) │ App iOS (Swift) │ App Android (Kotlin) │ 010 API│
└────────────────────────┬───────────────────────────────────────────┘
                         │ HTTPS / WSS
┌────────────────────────▼───────────────────────────────────────────┐
│  CAPA 2 — API GATEWAY + WAF                                        │
│  Kong/Traefik · OAuth2/OIDC · Rate limit · CCN-CERT WAF rules      │
└────────────────────────┬───────────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────────┐
│  CAPA 3 — ORQUESTACIÓN CONVERSACIONAL                              │
│  LangGraph · Intent router · Policy engine · Tool calling          │
└─────┬───────────┬──────────────┬────────────────────────┬──────────┘
      │           │              │                        │
┌─────▼────┐ ┌────▼──────┐ ┌─────▼───────┐ ┌──────────────▼────────┐
│ CAPA 4   │ │ CAPA 5    │ │ CAPA 6      │ │ CAPA 7                │
│ LLM      │ │ RAG       │ │ Herramientas│ │ Observabilidad        │
│ (vLLM)   │ │ (Milvus + │ │ (Citas,     │ │ (OpenTelemetry,       │
│ Salamandra│ │ BGE-M3)   │ │ Incidencias,│ │ Prometheus, Loki,     │
│ + Llama 4│ │           │ │ Padrón…)    │ │ Langfuse, SIEM)       │
└──────────┘ └───────────┘ └─────────────┘ └───────────────────────┘
```

## 3.2 Capa 1 — Canales

### 3.2.1 Widget web
- Implementación: **JavaScript vanilla** + Web Component (`<munibot-widget>`), peso ≤ 35 KB gzip.
- Sin dependencia de frameworks; compatible con CMS municipal (typo3, Drupal, AEM, WordPress).
- CSS aislado mediante Shadow DOM, tokens de diseño municipales personalizables.
- Soporta modo oscuro y modo alto contraste (WCAG 2.2 AA).
- Comunicación bidireccional vía **WebSocket** (WSS) para streaming de tokens.

### 3.2.2 Apps móviles
- **iOS**: SDK Swift Package Manager, requisitos iOS 16+.
- **Android**: SDK AAR (Maven), API mínima 26 (Android 8).
- Reutilizan el mismo backend conversacional.
- Capacidades nativas adicionales: geolocalización, cámara, biometría para sesión persistente, **push** vía APNS y FCM.
- Implementación offline-first parcial: caché de últimas 50 conversaciones y "intenciones frecuentes" precomputadas.

## 3.3 Capa 2 — API Gateway, WAF y Seguridad perimetral

- **Kong Gateway 3.x** o **Traefik 3** en alta disponibilidad (3 réplicas).
- **WAF**: ModSecurity con conjunto de reglas CRS + reglas específicas CCN-CERT (CCN-STIC-823).
- **Rate limit**: 60 mensajes/min por sesión anónima; 240 mensajes/min por sesión autenticada.
- **Autenticación**:
  - Anónima firmada por JWT corto (10 min, refresco automático).
  - Identificada vía **Cl@ve** (federación SAML/OIDC con la pasarela del Gobierno) para escenarios futuros con datos personales.
- **Anti-bot/DDoS**: integración con CloudPunch o equivalente on-premise (no se usan CDNs públicas externas con datos sensibles).
- **Detección de prompt injection** en gateway: filtros heurísticos + clasificador Llama Guard 3.

## 3.4 Capa 3 — Orquestación conversacional

El cerebro del sistema es un **grafo de estados conversacional** implementado con **LangGraph 0.4+**. Cada nodo del grafo representa una acción (consulta RAG, llamada a herramienta, generación libre, escalado), y las aristas se evalúan mediante un policy engine.

### 3.4.1 Componentes
| Componente | Función |
|---|---|
| Intent classifier | Modelo ligero (Salamandra-2B fine-tuned) clasifica entre 24 intenciones primarias. |
| Entity extractor | NER con FlairNLP-es para fechas, direcciones, importes, DNIs (con detección + redacción). |
| Policy engine | Reglas declarativas (OPA/Rego) que deciden si una pregunta puede contestarse, si necesita escalado humano o si se requiere autenticación. |
| Tool router | Selecciona la herramienta adecuada (RAG, API de citas, API de incidencias, búsqueda BOP). |
| Conversation memory | Memoria a corto plazo en Redis (sesión activa, máx. 30 turnos). |
| Guardrails | Llama Guard 3 + reglas propias para detectar contenido prohibido, política, violencia o información médica/legal vinculante. |

### 3.4.2 Patrón ReAct + Reflexión
Cada turno sigue el ciclo: **Razonar → Actuar → Observar → Responder → Reflexionar**. La reflexión genera un *self-check* sobre la respuesta antes de enviarla, descartando respuestas con baja confianza factual.

## 3.5 Capa 4 — Motor de inferencia LLM

### 3.5.1 Servidor de inferencia
**vLLM 0.7+** como motor principal por su madurez, soporte amplio de modelos y comunidad. Configuración:

- **PagedAttention** y **continuous batching**.
- **Speculative decoding** con un modelo borrador (Salamandra-2B) acelerando 1,6–1,9×.
- **Cuantización FP8** (H200) o **INT4 AWQ** para escenarios de máxima densidad.
- **Tensor parallelism** = 2 (modelo 70B) o 1 (modelos ≤ 14B).

**Alternativa**: **SGLang 0.4+** para cargas heavy-RAG (mejor *prefix caching*, hasta 29 % más throughput en modelos pequeños). Se desplegará un cluster SGLang específico para el clasificador y el reranker.

### 3.5.2 Topología de modelos

| Servicio | Modelo | Justificación |
|---|---|---|
| Clasificación de intención | Salamandra-2B-instruct fine-tuned | Bajo coste, latencia < 100 ms |
| Reranker semántico | BGE-Reranker-v2-m3 | Mejora 6–9 pp la precisión del RAG |
| Generación principal | Salamandra-7B-Instruct + Llama 4 Scout fallback | Español nativo, ENS-compatible |
| Generación compleja | Qwen 3.5 14B / Llama 4 Maverick | Razonamiento, redacción legal |
| Guardrails | Llama Guard 3 8B | Seguridad de contenidos |

## 3.6 Capa 5 — Pipeline RAG

### 3.6.1 Ingesta y normalización del corpus
Fuentes oficiales (frecuencia de actualización):

| Fuente | Frecuencia | Volumen estimado |
|---|---|---|
| Web del ayuntamiento | Diaria (crawler) | ≈ 12.000 URLs |
| Sede electrónica (catálogo de trámites) | Diaria (API) | ≈ 850 trámites |
| Ordenanzas municipales | Semanal (PDF) | ≈ 230 documentos |
| Boletín Oficial de la Provincia (BOP) – sección municipal | Diaria | ≈ 40.000 entradas/año |
| Plenos y actas | Tras publicación | ≈ 36/año |
| FAQ curadas por servicio de atención | Continua | ≈ 4.500 entradas |
| Datos abiertos (open data) | Diaria (CKAN) | ≈ 350 datasets |

### 3.6.2 Procesamiento
1. **Extracción**: Apache Tika + Unstructured.io (para PDF, DOCX, HTML, ODT).
2. **Limpieza**: eliminación de menús, footers, normalización de unicode.
3. **Chunking**: estrategia híbrida — semántico para texto continuo, estructural para tablas y formularios. Tamaño objetivo 512 tokens, solapamiento 64.
4. **Enriquecimiento**: metadatos (URL fuente, fecha, sección, tipo de documento, ámbito territorial, idioma).
5. **Embedding**: **BGE-M3** (1.024 dimensiones, multilingüe, hasta 8.192 tokens).
6. **Indexación**: vector store **Milvus 2.5** (HNSW + scalar quantization) + índice invertido **OpenSearch 2.x** para BM25 / búsqueda léxica híbrida.
7. **Versionado**: cada cambio en el corpus se versiona con DVC; rollback granular por documento.

### 3.6.3 Retrieval
Estrategia híbrida con tres pasos:

1. **Recall amplio**: top-50 por similitud densa (BGE-M3) + top-50 por BM25 → fusión RRF (Reciprocal Rank Fusion).
2. **Rerank**: top-50 → top-8 con BGE-Reranker-v2-m3.
3. **Filtro de frescura y permisos**: descarta documentos derogados, fuera de ámbito o con visibilidad restringida.

## 3.7 Capa 6 — Herramientas (tool calling)

Las herramientas se exponen como microservicios internos con esquema OpenAPI 3.1 documentado. El LLM las invoca vía *function calling* nativo de los modelos soportados.

| Herramienta | Backend | Función |
|---|---|---|
| `consultar_tramite(id)` | Sede electrónica | Devuelve ficha estructurada del trámite. |
| `disponibilidad_cita(servicio, oficina, fecha)` | CRM/Citas | Devuelve huecos disponibles. |
| `reservar_cita(servicio, oficina, slot, contacto)` | CRM/Citas | Crea cita y devuelve justificante. |
| `crear_incidencia(tipo, lat, lon, descripcion, foto?)` | GIS incidencias | Crea ticket y devuelve número de seguimiento. |
| `estado_incidencia(ticket_id)` | GIS incidencias | Consulta estado y plazo. |
| `buscar_bop(query, fecha_desde, fecha_hasta)` | BOP API | Búsqueda en boletín oficial. |
| `geocodificar(direccion)` | Cartociudad / propio | Devuelve coordenadas y entidad administrativa. |
| `derivar_humano(motivo, transcripcion)` | Contact Center | Crea ticket y enruta al canal del operador. |

## 3.8 Capa 7 — Observabilidad, evaluación y operación

| Función | Herramienta open source |
|---|---|
| Métricas | Prometheus + Grafana |
| Logs | Loki + Grafana |
| Trazas distribuidas | OpenTelemetry + Tempo |
| Trazabilidad de conversaciones LLM | **Langfuse** (self-hosted) |
| SIEM | Wazuh + integración CCN-CERT |
| Evaluación continua de calidad | Ragas + DeepEval (pipelines nocturnos) |
| Detección de drift | Evidently AI |
| Gestión de incidencias | GLPI o Zammad |

### 3.8.1 Evaluación continua
Cada noche se ejecuta un **golden set** de 1.200 preguntas-respuesta validadas por personal municipal, midiendo:

- Precisión factual (exact match + LLM-as-judge calibrado).
- Cobertura RAG (cuántos chunks recuperados realmente contienen la respuesta).
- Latencia P50/P95/P99.
- Tasa de alucinación (claims sin soporte en contexto).
- Cumplimiento de tono institucional.

## 3.9 Diagrama de despliegue lógico

```
┌─ Zona de exposición (DMZ) ──────────────────────────────────────┐
│  Balanceador HAProxy ─── WAF ── API Gateway (3x)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ mTLS
┌─ Zona interna de aplicación ────────────────────────────────────┐
│  Kubernetes (RKE2/OpenShift)                                    │
│  ├─ Orquestador (LangGraph) x3                                  │
│  ├─ Inferencia LLM (vLLM) x N nodos GPU                         │
│  ├─ Reranker / Clasificador (SGLang) x2                         │
│  ├─ RAG service (FastAPI) x3                                    │
│  ├─ Tools microservicios x N                                    │
│  └─ Worker async (Celery / Arq) x2                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌─ Zona de datos ─────────────────────────────────────────────────┐
│  Milvus (vector store) · OpenSearch · PostgreSQL ·              │
│  Redis (cache/sesión) · MinIO (objetos) · Kafka (eventos)       │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─ Zona de gestión ───────────────────────────────────────────────┐
│  CI/CD (Forgejo + Drone) · Vault (secretos) · Backup (Restic)   │
│  Monitoring · SIEM · Langfuse                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 3.10 Integraciones externas (sistemas municipales)

| Sistema | Propósito | Protocolo |
|---|---|---|
| Sede electrónica | Catálogo de trámites, estado de expediente | REST + OAuth2 |
| Registro electrónico (ORVE/GEISER) | Presentación de instancias | SOAP/REST según versión |
| Padrón municipal | Verificación de empadronamiento (futuro) | REST + Cl@ve |
| Sistema de citas (TUPI/CITA-Q o propio) | Reserva | REST |
| Sistema de incidencias (Línea Verde, MOSAIC, propio) | Tickets | REST |
| GIS municipal (ArcGIS / QGIS Server / Geoserver) | Datos geoespaciales | OGC WMS/WFS |
| BOP | Búsqueda normativa local | REST + scraping respetuoso |
| Cl@ve / FNMT | Identidad digital | SAML2 / OIDC |
| Contact center (Genesys / Avaya / Asterisk) | Escalado a operador humano | WebRTC + REST |

## 3.11 Patrón de despliegue: alta disponibilidad y blue-green

- Dos zonas de despliegue (CPD principal + CPD secundario a > 40 km).
- **Activo-activo** con balanceo geográfico (GSLB DNS interno).
- **Despliegues blue-green** para el modelo: cada actualización se valida con tráfico sombra (5 %) y *canary* (15 %) antes de la promoción.
- **Backups**: PostgreSQL WAL streaming + snapshots Milvus diarios + replicación MinIO entre CPDs.
- **DRP**: RTO 4 h, RPO 15 min. Simulacro semestral.
