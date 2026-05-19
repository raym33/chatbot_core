# 1. RESUMEN EJECUTIVO

## 1.1 Visión del proyecto

El presente documento describe el prototipo y estudio de viabilidad de un **asistente conversacional basado en Inteligencia Artificial Generativa** para un ayuntamiento de aproximadamente **1.000.000 de habitantes** en España. La solución se diseña para ser desplegada **íntegramente en infraestructura local (on-premise)** del consistorio, utilizando **exclusivamente modelos de lenguaje de código abierto (open source)**, garantizando así la **soberanía del dato**, el cumplimiento del **Esquema Nacional de Seguridad (ENS) en categoría ALTA**, el **Reglamento General de Protección de Datos (RGPD)** y el **Reglamento Europeo de Inteligencia Artificial (AI Act)** que entra en plena aplicación para sistemas de alto riesgo el 2 de agosto de 2026.

El asistente estará disponible en dos canales:

- **Sede electrónica / portal web** del ayuntamiento, mediante un widget embebido.
- **Aplicación móvil oficial** (iOS y Android), mediante SDK nativo conectado al mismo backend.

## 1.2 Alcance funcional

El prototipo cubre tres dominios funcionales priorizados:

1. **Información general municipal**: trámites, horarios, ubicaciones, tasas, normativa local, agenda cultural, transporte, padrón, urbanismo, FAQs.
2. **Cita previa**: consulta de disponibilidad, reserva, modificación y cancelación de citas en oficinas de atención ciudadana, registro civil, urbanismo, recaudación y servicios sociales.
3. **Incidencias urbanas**: reporte ciudadano de incidencias (alumbrado, limpieza viaria, baches, mobiliario urbano, ruidos, parques y jardines) con geolocalización y posibilidad de adjuntar fotografía.

Quedan **fuera del alcance** de esta primera fase los trámites que requieren autenticación fuerte (Cl@ve / certificado digital) sobre datos personales sensibles (consulta de multas, IBI, padrón individual), que se contemplan como **Fase 2** una vez validado el piloto.

## 1.3 Principios rectores

| Principio | Aplicación |
|---|---|
| **Soberanía digital** | 100% on-premise, sin envío de datos a terceros ni a la nube. |
| **Open source** | Modelos con licencia permisiva (Apache 2.0, MIT, Llama Community). |
| **Privacidad por diseño** | Anonimización en origen, sin retención de PII por defecto. |
| **Transparencia algorítmica** | Conforme al art. 50 del AI Act: el ciudadano sabe que habla con una IA. |
| **Accesibilidad universal** | Cumplimiento EN 301 549, WCAG 2.2 AA, lectura fácil. |
| **Sostenibilidad** | Inferencia eficiente (cuantización FP8/INT4) y compartición de GPU. |
| **Reversibilidad** | Arquitectura modular, sin dependencia de proveedor único. |

## 1.4 Tecnología propuesta (alto nivel)

- **Modelo de lenguaje principal**: **Salamandra-7B-Instruct** (Barcelona Supercomputing Center, Apache 2.0) optimizado para español y lenguas cooficiales, complementado con **Llama 4 Scout** o **Qwen 3.5 14B** para razonamiento complejo en escenarios de alta carga.
- **Modelo de embeddings**: **BGE-M3** (multilingüe, hasta 8.192 tokens) para indexación y recuperación semántica.
- **Arquitectura**: **Retrieval Augmented Generation (RAG)** con base de conocimiento municipal versionada, motor de inferencia **vLLM** y orquestación con LangGraph.
- **Hardware**: Cluster de **2 nodos** con **8 GPUs NVIDIA H200** cada uno (HBM3e 141 GB) en alta disponibilidad activo-activo, ubicado en el CPD municipal o en un CPD certificado ENS-Alto.
- **Pila de seguridad**: Cifrado AES-256 en reposo y TLS 1.3 en tránsito, HSM, SIEM con CCN-CERT, registro inmutable de auditoría.

## 1.5 Beneficios esperados

| Indicador | Situación actual estimada | Objetivo con el chatbot |
|---|---|---|
| Llamadas al 010/centralita | ~2.500.000/año | Reducción del 30 % (-750.000) |
| Tiempo medio de respuesta a una FAQ | 4–8 minutos (presencial/teléfono) | < 5 segundos (24/7) |
| Trámites iniciados fuera de horario | < 5 % | > 40 % |
| Satisfacción ciudadana (CSAT) | 6,8/10 | > 8,2/10 |
| Coste por interacción atendida | 4,50 € (presencial) / 2,80 € (telefónica) | 0,18 € (chatbot) |
| Disponibilidad del servicio | L–V 8:30–14:00 | 24×7×365 |

## 1.6 Coste estimado (visión global)

| Concepto | Importe (€, IVA excl.) |
|---|---|
| **CAPEX – Inversión inicial (hardware + licencias OSS + integración)** | **1.180.000 €** |
| **OPEX anual (operación, mantenimiento, energía, personal)** | **295.000 €/año** |
| **TCO a 5 años** | **2.655.000 €** |
| **Coste por interacción (año 3, en régimen)** | **0,18 €** |
| **Ahorro neto estimado a 5 años vs. canales tradicionales** | **3,9 – 5,2 M €** |

El **retorno de la inversión (ROI)** se sitúa en torno a los **22–26 meses** desde la puesta en producción, asumiendo una adopción del 35 % de la base ciudadana en el primer año.

## 1.7 Comparativa frente a soluciones SaaS comerciales

Frente a alternativas de tipo Azure OpenAI Service, Google Vertex AI o AWS Bedrock, la solución on-premise propuesta:

- **Elimina** el riesgo regulatorio de transferencias internacionales de datos (Schrems II, cláusulas tipo).
- **Suprime** el coste variable por token (que en el escenario de 1 M de habitantes con 12 M de consultas/año supondría entre 1,8 y 3,5 M €/año en SaaS).
- **Garantiza** la trazabilidad completa del modelo, datos de entrenamiento y comportamiento.
- **Permite** afinar (fine-tuning) sobre normativa, ordenanzas y lenguaje propio del municipio sin restricciones.

El sobrecoste inicial del modelo on-premise (CAPEX más alto) se amortiza en **menos de 18 meses** únicamente con el ahorro de licencias SaaS.

## 1.8 Riesgos críticos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Alucinaciones del modelo en información oficial | Alta | Alto | RAG estricto + respuestas con citas + escalado a humano |
| Sesgo lingüístico o sociodemográfico | Media | Alto | Auditoría algorítmica anual + evaluación con DiscrIA |
| Caída del CPD principal | Baja | Crítico | Cluster activo-activo en dos CPDs + DRP < 4 h RTO |
| No clasificación correcta bajo AI Act | Media | Alto | DPIA + FRIA + registro UE de sistemas de alto riesgo |
| Saturación en picos (>500 sesiones simultáneas) | Media | Medio | Autoescalado horizontal + cola con SLA degradado |

## 1.9 Conclusión y recomendación

El estudio concluye que el despliegue **es técnicamente viable, económicamente rentable y legalmente compatible** con el marco normativo español y europeo. Se recomienda iniciar un **piloto controlado de 6 meses** sobre el dominio de información general (FAQs) antes de incorporar gestión de citas e incidencias, con métricas claras de aceptación y un comité de gobernanza algorítmica multidisciplinar (informática, jurídica, atención ciudadana, accesibilidad y delegado de protección de datos).
