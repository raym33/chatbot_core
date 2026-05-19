# 2. CASOS DE USO Y REQUISITOS

## 2.1 Contexto y población objetivo

El municipio cuenta con aproximadamente **1.000.000 de habitantes**, de los cuales se estiman:

- **820.000** mayores de 16 años (potenciales usuarios directos).
- **78 %** con acceso a internet móvil (≈ 640.000).
- **62 %** han realizado al menos un trámite electrónico con la administración local en los últimos 12 meses.
- **41.000** empresas y autónomos con domicilio fiscal en el municipio.
- **15.000** turistas/visitantes en estancias cortas durante temporada alta.

Sobre esta base se estima una demanda objetivo de:

| Métrica | Año 1 (piloto) | Año 2 | Año 3 (régimen) |
|---|---|---|---|
| Usuarios únicos activos / mes | 35.000 | 120.000 | 220.000 |
| Sesiones / mes | 80.000 | 360.000 | 1.000.000 |
| Mensajes / mes | 320.000 | 1.700.000 | 4.800.000 |
| Pico concurrente (sesiones simultáneas) | 150 | 450 | 900 |
| Mensajes/día medio | 10.500 | 56.000 | 160.000 |

## 2.2 Personas tipo (user personas)

### Persona 1: Carmen, 67 años
Pensionada, alfabetización digital media-baja. Necesita resolver consultas sobre cita en el centro de salud municipal y tarjeta de transporte para personas mayores. Usa principalmente el móvil con texto grande. **Requiere accesibilidad reforzada y lectura fácil.**

### Persona 2: David, 34 años
Profesional autónomo. Quiere consultar el estado de su licencia de obra, pedir cita en urbanismo y reportar un bache en la calle de su negocio. **Requiere rapidez, integración con sede electrónica y notificaciones push.**

### Persona 3: Aisha, 28 años
Recién empadronada, lengua materna árabe pero residente con buen castellano. Necesita información sobre cómo escolarizar a su hijo, ayudas al alquiler y cursos de formación. **Requiere lenguaje claro, sin jerga administrativa, con enlaces a oficina presencial si lo pide.**

### Persona 4: Equipo de prensa municipal
Usuario interno. Consulta el chatbot como herramienta de soporte para preparar notas de prensa con datos oficiales actualizados. **Requiere modo "experto" con citas verificables.**

## 2.3 Casos de uso detallados

### CU-01 — Consulta de información general (FAQ)

**Actor**: Ciudadano (anónimo o identificado).
**Precondición**: Acceso al canal web o app.
**Flujo principal**:
1. El ciudadano abre el widget/app y plantea la consulta en lenguaje natural.
2. El sistema clasifica la intención y recupera fragmentos relevantes del corpus municipal (RAG).
3. Genera respuesta con citas a la fuente oficial (BOP, ordenanza, página web del ayuntamiento).
4. Ofrece acciones posibles: «Pedir cita», «Ver en mapa», «Llamar al 010», «Contactar con un agente».

**Ejemplos reales**:
- «¿Cuándo se paga el IBI este año?»
- «¿Qué necesito para empadronarme si vengo de otro país?»
- «¿A qué hora abre la biblioteca de Tetuán los sábados?»
- «¿Hay zona azul en la calle Mayor?»

**Volumen esperado**: 78 % del tráfico total.

### CU-02 — Gestión de cita previa

**Actor**: Ciudadano.
**Precondición**: Servicio de cita disponible en el área solicitada.
**Flujo principal**:
1. El ciudadano expresa la necesidad: «Quiero pedir cita para renovar el DNI» / «Cambiar la titularidad de un vado».
2. El sistema desambigua el servicio concreto y la oficina más cercana (geolocalización con consentimiento).
3. Consulta disponibilidad vía API del módulo de citas del CRM municipal.
4. Propone 3 huecos disponibles. Confirma la reserva.
5. Envía recordatorio por SMS/email/push 24h antes de la cita.

**Variantes**:
- Modificación de cita existente (autenticación ligera con DNI + email/teléfono verificado).
- Cancelación.
- Lista de espera si no hay huecos.

**Volumen esperado**: 14 % del tráfico.

### CU-03 — Reporte de incidencia urbana

**Actor**: Ciudadano.
**Precondición**: Permisos de geolocalización y cámara concedidos (opcional).
**Flujo principal**:
1. «Hay una farola fundida en mi calle.»
2. El sistema solicita: tipología (multi-opción), ubicación (geolocalización o dirección manual), foto opcional.
3. Crea un ticket en el sistema de incidencias municipal (p. ej. **Línea Verde**, **GIS corporativo** o equivalente) con identificador único.
4. Informa del plazo estimado de resolución según el tipo y prioridad.
5. Permite seguimiento del ticket por su número.

**Tipologías predefinidas**: alumbrado, limpieza viaria, recogida de residuos, mobiliario urbano, jardinería, baches y firme, semáforos, ruido, animales, vandalismo.

**Volumen esperado**: 8 % del tráfico.

### CU-04 — Escalado a agente humano

**Actor**: Ciudadano y operador del 010 / oficina de atención.
**Precondición**: El sistema detecta que no puede resolver o el ciudadano lo solicita.
**Flujo principal**:
1. Disparadores: baja confianza del modelo (< 0,55), tema sensible (servicios sociales, violencia de género, vivienda), tres reformulaciones del usuario sin éxito, petición explícita («quiero hablar con una persona»).
2. El sistema entrega al operador la transcripción anonimizada, la intención detectada y los pasos ya intentados.
3. El operador continúa la conversación sin que el ciudadano deba repetir contexto.

## 2.4 Requisitos funcionales (RF)

| Código | Descripción | Prioridad |
|---|---|---|
| RF-01 | Conversación en español natural, con tolerancia a faltas de ortografía. | Crítica |
| RF-02 | Recuperación aumentada (RAG) con corpus municipal versionado. | Crítica |
| RF-03 | Citación de la fuente oficial en respuestas factuales. | Crítica |
| RF-04 | Integración con el sistema de cita previa municipal. | Alta |
| RF-05 | Integración con el sistema de incidencias urbanas (GIS). | Alta |
| RF-06 | Escalado a agente humano con contexto. | Alta |
| RF-07 | Geolocalización opcional con consentimiento explícito. | Alta |
| RF-08 | Soporte de adjuntos: imagen (JPG/PNG/HEIC ≤ 10 MB). | Media |
| RF-09 | Modo lectura fácil seleccionable por el usuario. | Alta |
| RF-10 | Histórico de conversación del usuario (si está autenticado, máx. 90 días). | Media |
| RF-11 | Métricas en tiempo real para el cuadro de mando municipal. | Alta |
| RF-12 | Panel de administración para edición y publicación del corpus. | Crítica |
| RF-13 | Notificaciones push y email para recordatorios y respuestas asíncronas. | Media |
| RF-14 | Aviso al inicio de cada sesión: «Está conversando con una IA municipal» (AI Act art. 50). | Crítica |
| RF-15 | Botón permanente de feedback (👍/👎 + texto libre). | Alta |

## 2.5 Requisitos no funcionales (RNF)

| Código | Categoría | Métrica |
|---|---|---|
| RNF-01 | Disponibilidad | 99,9 % anual (SLA 8,76 h indisponibilidad/año) |
| RNF-02 | Latencia P95 (primer token) | < 1,2 s |
| RNF-03 | Latencia P95 (respuesta completa media de 200 tok.) | < 4,0 s |
| RNF-04 | Throughput agregado | ≥ 5.000 tokens/s sostenido por nodo |
| RNF-05 | Concurrencia pico | 900 sesiones simultáneas sin degradación |
| RNF-06 | Escalabilidad horizontal | +1 nodo en < 30 min sin downtime |
| RNF-07 | Cumplimiento ENS | Categoría ALTA certificada |
| RNF-08 | Cumplimiento RGPD/LOPDGDD | DPIA aprobada por DPD municipal |
| RNF-09 | Cumplimiento AI Act | Registro como sistema alto riesgo + FRIA |
| RNF-10 | Accesibilidad | EN 301 549 + WCAG 2.2 AA |
| RNF-11 | Idioma | Castellano (100 %), arquitectura preparada para añadir lenguas cooficiales |
| RNF-12 | Retención de datos | PII anonimizada < 24 h, conversaciones anonimizadas ≤ 12 meses |
| RNF-13 | Trazabilidad | Log inmutable de cada interacción con hash encadenado |
| RNF-14 | RTO / RPO | RTO ≤ 4 h, RPO ≤ 15 min |
| RNF-15 | Sostenibilidad | PUE del CPD ≤ 1,3; uso de GPU compartida vía MIG |

## 2.6 KPIs operativos y de calidad

| Categoría | KPI | Objetivo año 1 | Objetivo régimen |
|---|---|---|---|
| Adopción | Tasa de penetración sobre población > 16 | 8 % | 35 % |
| Adopción | Sesiones por usuario activo/mes | 1,8 | 3,5 |
| Calidad | Tasa de resolución sin escalado | ≥ 65 % | ≥ 82 % |
| Calidad | Precisión factual (auditada mensual) | ≥ 92 % | ≥ 96 % |
| Calidad | Alucinación detectada por revisión humana | < 4 % | < 1,5 % |
| Calidad | CSAT (👍 sobre total valoradas) | ≥ 78 % | ≥ 88 % |
| Operación | Tickets de incidencia creados correctamente | ≥ 95 % | ≥ 99 % |
| Operación | Citas confirmadas/intentos | ≥ 90 % | ≥ 97 % |
| Eficiencia | Coste medio por interacción | ≤ 0,35 € | ≤ 0,18 € |
| Equidad | Diferencia CSAT por edad (>65 vs media) | ≤ 8 pp | ≤ 4 pp |
