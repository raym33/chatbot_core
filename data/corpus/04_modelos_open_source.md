# 4. SELECCIÓN DE MODELOS OPEN SOURCE

## 4.1 Criterios de selección

La elección de cada modelo se rige por cinco criterios ponderados:

| Criterio | Peso | Descripción |
|---|---|---|
| **Licencia** | 25 % | Compatible con uso en administración pública (Apache 2.0, MIT, Llama Community Aceptable). |
| **Calidad en español** | 25 % | Benchmark MMLU-es, FLORES-200 es↔en, evaluación humana propia. |
| **Tamaño y eficiencia** | 20 % | Relación calidad/coste de inferencia, soporte cuantización FP8/INT4. |
| **Transparencia** | 15 % | Datos de entrenamiento documentados, evaluación de sesgos, model card completa. |
| **Soporte de tooling/función** | 15 % | Function calling, JSON estructurado, soporte vLLM/SGLang. |

## 4.2 Panorama de modelos open source (mayo 2026)

En los últimos 12 meses se han publicado al menos cinco familias open-weight de frontera relevantes para el caso de uso:

| Familia | Fabricante | Tamaños | Licencia | Fortalezas |
|---|---|---|---|---|
| **Llama 4** (Scout / Maverick) | Meta | 17B-A / 109B-A MoE | Llama 4 Community | Razonamiento, function calling maduro |
| **Qwen 3.5** | Alibaba | 0.6B – 235B-A22B | Apache 2.0 (la mayoría) | Multilingüe líder, eficiencia en MoE |
| **DeepSeek V4** (Pro/Flash) | DeepSeek | 671B-A37B | MIT (pesos) | Capacidad bruta, contexto 1M |
| **Gemma 4** | Google | 2B – 27B | Gemma TOU | On-device, eficiencia |
| **Mistral Medium 3.5** | Mistral AI | 70B aprox. | Apache 2.0 / Mistral Research | EU-friendly, código y razonamiento |
| **Salamandra** | BSC (España) | 2B / 7B / 40B | Apache 2.0 | Especializado en lenguas oficiales de España |
| **EuroLLM 9B** | Consorcio europeo | 9B / 22B | Apache 2.0 | Cobertura 35 lenguas de la UE |

## 4.3 Modelo principal recomendado: Salamandra

### 4.3.1 Justificación

**Salamandra**, desarrollado por el **Barcelona Supercomputing Center (BSC-CNS)**, es el modelo más adecuado para esta solución por cuatro razones decisivas:

1. **Soberanía española y europea**: entrenado en MareNostrum 5 (EuroHPC), financiado con fondos públicos y plenamente alineado con la estrategia España Digital 2026.
2. **Calidad nativa en español, catalán, euskera, gallego y occitano**: corpus priorizado en lenguas oficiales del Estado, con un 18-22 % del entrenamiento en estas lenguas (frente a < 3 % en modelos americanos o chinos).
3. **Licencia Apache 2.0**: la más permisiva, sin restricciones de uso comercial ni cláusulas territoriales.
4. **Transparencia total**: dataset documentado, scripts de entrenamiento públicos en GitHub, technical report en arXiv, model cards exhaustivas.

### 4.3.2 Variantes elegidas

| Modelo | Uso | Tamaño VRAM (FP8) |
|---|---|---|
| **salamandra-2b-instruct** | Clasificación de intención, NER, generación rápida | ≈ 2,5 GB |
| **salamandra-7b-instruct** | Generación principal en conversaciones diarias | ≈ 8 GB |
| **salamandra-7b-base-fp8** | Base para fine-tuning municipal | ≈ 8 GB |
| **salamandraTA-7b-instruct** | Traducción cooficial (catalán/euskera/gallego ↔ es) si se activa Fase 2 | ≈ 8 GB |

## 4.4 Modelo de refuerzo: Llama 4 Scout

Para escenarios que requieren **razonamiento complejo, redacción legal formal o respuestas largas** (p. ej. resúmenes de ordenanza, comparativas de tasas), se enruta dinámicamente a **Llama 4 Scout** (17B activos sobre 109B totales en arquitectura MoE).

### Razones para mantenerlo como secundario y no principal

- Licencia *Llama 4 Community* tiene restricciones (cláusulas territoriales por encima de 700M MAU; no aplican al caso pero condicionan auditoría).
- Aunque su español es excelente, su corpus priorizado es inglés.
- Su coste de inferencia es mayor (109B params totales, requiere shard en 2 GPUs H200).

Se usará bajo enrutamiento con umbral: si la consulta supera un score de complejidad > 0,72 (medido por longitud, presencia de cláusulas condicionales, peticiones legales), se deriva a Llama 4 Scout.

## 4.5 Modelo de embeddings: BGE-M3

| Característica | BGE-M3 | Alternativas evaluadas |
|---|---|---|
| Idiomas | 100+ (excelente español) | Jina v3 (89), E5-large (100) |
| Modos | Denso + sparse + multi-vector | Denso solo |
| Long context | 8.192 tokens | 8.192 (Jina), 512 (E5) |
| Parámetros | 568M | 570M (Jina), 560M (E5-large) |
| Licencia | MIT | Apache (Jina v3) / MIT (E5) |
| Rendimiento MTEB-es | 71,8 | 70,2 (Jina v3) / 68,4 (E5-large) |

Se selecciona **BGE-M3** por su combinación única de embedding **denso + sparse + multivector** en un único pase, que habilita búsqueda híbrida nativa y reduce coste operativo. Como **reranker** se utiliza **BGE-Reranker-v2-m3** (similar familia).

## 4.6 Modelo de guardrails: Llama Guard 3 8B

- Clasifica entradas y salidas en 14 categorías de riesgo (violencia, autolesión, contenido sexual, discriminación, asesoramiento médico/legal vinculante, etc.).
- Latencia < 200 ms en H200.
- Personalizable con políticas en lenguaje natural ("no respondas sobre filiación política", "no asesores en disputas vecinales privadas").

## 4.7 Otros modelos auxiliares (opcionales en Fase 2)

| Función | Modelo | Notas |
|---|---|---|
| Reconocimiento de voz (canal telefónico) | **Whisper Large v3** (OpenAI, MIT) | Excelente español, soporta dialectos |
| Síntesis de voz | **Coqui XTTS v2** o **Piper** | Voz natural en castellano |
| OCR de documentos adjuntos | **PaddleOCR** + **DocLing** | Para procesar instancias escaneadas |
| Visión (analizar foto de incidencia) | **Qwen2.5-VL 7B** o **Llama 4 Maverick VL** | Identificar tipo de incidencia desde foto |

## 4.8 Comparativa cualitativa final

| Tarea | Modelo elegido | Razón principal |
|---|---|---|
| Clasificación de intención | Salamandra-2B | Latencia y coste mínimos |
| Generación principal (FAQs, conversación) | Salamandra-7B-Instruct | Español de calidad + soberanía |
| Generación compleja (razonamiento legal) | Llama 4 Scout | Razonamiento avanzado |
| Embeddings | BGE-M3 | Híbrido denso+sparse |
| Reranking | BGE-Reranker-v2-m3 | Coherencia con embeddings |
| Guardrails | Llama Guard 3 8B | Estado del arte open |
| Visión (Fase 2) | Qwen2.5-VL 7B | Buen español + multimodal |

## 4.9 Estrategia de actualización de modelos

- **Catálogo interno de modelos** versionado en MinIO + Hugging Face mirror local (sin acceso externo en producción).
- Cada modelo se evalúa contra el golden set municipal antes de su promoción.
- Política de versionado **N-1**: siempre se mantiene la versión anterior cargada en pre-producción durante 90 días para rollback inmediato.
- Cadencia de revisión trimestral del catálogo (nuevos modelos open source, nuevas versiones, retirada de versiones obsoletas).

## 4.10 Fine-tuning municipal

Se prevé un fine-tuning ligero (LoRA r=16) sobre Salamandra-7B-Instruct con:

- 25.000 pares pregunta-respuesta validados por personal de atención ciudadana.
- 8.000 ejemplos de tono institucional (formales, neutros, respetuosos).
- 4.000 ejemplos de redirección (cuándo NO responder).

El fine-tuning se ejecuta en el propio cluster en 8-12 horas. Genera un adaptador LoRA de ≈ 180 MB que se carga junto al modelo base, sin necesidad de re-deploy completo.
