# 6. SEGURIDAD, PRIVACIDAD Y CUMPLIMIENTO

## 6.1 Marco normativo aplicable

| Norma | Ámbito | Implicación |
|---|---|---|
| **Reglamento (UE) 2024/1689 – AI Act** | UE | Sistema de alto riesgo (Anexo III, punto 5: servicios públicos esenciales). Aplicación 2 ago 2026. |
| **Reglamento (UE) 2016/679 – RGPD** | UE | Tratamiento de datos personales. |
| **LO 3/2018 LOPDGDD** | España | Adaptación nacional del RGPD. |
| **Real Decreto 311/2022 – ENS** y RD posteriores 2025/2026 | España | Categoría ALTA obligatoria por dependencia critica del servicio. |
| **Real Decreto 4/2010 – ENI** | España | Esquema Nacional de Interoperabilidad. |
| **Ley 39/2015 PAC** y **40/2015 RJSP** | España | Procedimiento administrativo electrónico. |
| **Ley 19/2013 – Transparencia** | España | Publicidad activa del sistema. |
| **EN 301 549 v3.2.1** | UE | Accesibilidad TIC (transposición Directiva 2016/2102). |
| **ISO/IEC 27001:2022 + 27701:2019** | Internacional | SGSI y gestión de privacidad. |
| **ISO/IEC 42001:2023** | Internacional | Sistema de gestión de IA. |

## 6.2 AI Act — clasificación y obligaciones

### 6.2.1 Clasificación del sistema

El chatbot municipal se clasifica como **sistema de IA de alto riesgo** porque:

- Es un sistema utilizado por una **autoridad pública** para prestar servicios esenciales (Anexo III, apartado 5(a)).
- Puede influir en el acceso a servicios públicos (cita previa, asistencia social futura).
- Adicionalmente está sujeto a obligaciones de **transparencia** del artículo 50, al interactuar directamente con personas físicas.

### 6.2.2 Obligaciones del proveedor (ayuntamiento o adjudicatario)

| Obligación | Cómo se cumple |
|---|---|
| Sistema de gestión de riesgos continuo (art. 9) | Comité de gobernanza, registro de riesgos vivo, revisión trimestral |
| Calidad de los datos (art. 10) | Corpus auditado, gobernanza del dato, controles de sesgos |
| Documentación técnica (art. 11, Anexo IV) | Dossier técnico completo (este documento + anexos) |
| Registro automático de eventos (art. 12) | Logs inmutables 36 meses, trazabilidad por interacción |
| Transparencia hacia usuarios (art. 13, 50) | Aviso "Está hablando con una IA" + acceso a documentación pública |
| Supervisión humana (art. 14) | Botón de escalado humano siempre disponible + revisión muestral diaria |
| Precisión, robustez, ciberseguridad (art. 15) | Evaluación continua, redundancia, pen-tests anuales |
| FRIA (Evaluación Impacto Derechos Fundamentales, art. 27) | Realizada y publicada antes de la puesta en producción |
| Registro UE de sistemas de alto riesgo (art. 49, 71) | Inscripción en la base de datos europea |

### 6.2.3 Marca CE y declaración UE de conformidad

Antes de la puesta en producción, el sistema debe disponer de:

- **Declaración UE de conformidad** firmada por el responsable del ayuntamiento.
- **Marcado CE** virtual en la documentación.
- **Evaluación de conformidad** por procedimiento interno (Anexo VI), salvo que se modifique el régimen para sistemas del sector público.

## 6.3 RGPD — Tratamientos y bases legales

### 6.3.1 Tratamientos identificados

| Tratamiento | Base legal | Plazo |
|---|---|---|
| Conversación anónima (sin identificar al ciudadano) | Interés público (art. 6.1.e) | 90 días en claro, hasta 12 meses anonimizada |
| Conversación identificada (Cl@ve, futuro) | Cumplimiento misión de interés público | Según plazos del procedimiento administrativo asociado |
| Geolocalización para incidencias | Consentimiento explícito (art. 6.1.a) | Ligada a vida del ticket |
| Fotos adjuntas | Consentimiento explícito | Ligada a vida del ticket, eliminada tras cierre |
| Histórico para entrenamiento/mejora | Interés legítimo + anonimización irreversible | Datos sintetizados, originales eliminados |

### 6.3.2 Principios aplicados

- **Minimización**: solo se almacena lo imprescindible. PII se redacta antes de persistir.
- **Limitación de finalidad**: los datos no se usan para evaluación ciudadana ni perfilado.
- **Exactitud**: corpus auditado, mecanismos de rectificación (botón "esta información no es correcta").
- **Limitación del plazo**: políticas de retención automatizadas con TTL.
- **Integridad y confidencialidad**: cifrado en reposo (AES-256-GCM) y en tránsito (TLS 1.3 + mTLS).
- **Responsabilidad proactiva**: trazabilidad inmutable + auditorías independientes.

### 6.3.3 DPIA (Data Protection Impact Assessment)

Es **obligatoria** (art. 35 RGPD). Cubre:

- Descripción del tratamiento y flujos.
- Necesidad y proporcionalidad.
- Riesgos para derechos y libertades.
- Medidas técnicas y organizativas para mitigar.
- Consulta al DPD municipal (Delegado de Protección de Datos).

Se firma por el responsable del tratamiento (ayuntamiento) antes del piloto.

### 6.3.4 Derechos de los interesados

- **Acceso, rectificación, supresión, limitación, oposición, portabilidad** se ejercen ante el DPD por los canales habituales del ayuntamiento.
- **Derecho a no ser objeto de decisión automatizada (art. 22 RGPD)**: el chatbot no toma decisiones administrativas. Todas las decisiones con efectos jurídicos están reservadas a personal humano competente.

## 6.4 ENS Categoría ALTA

### 6.4.1 Justificación de la categoría

Cumple los criterios de categoría ALTA por:

- **Disponibilidad**: la indisponibilidad prolongada (>24 h) tendría impacto público notorio.
- **Integridad**: una manipulación de respuestas podría inducir errores administrativos masivos.
- **Trazabilidad**: necesaria para rendición de cuentas algorítmica.

### 6.4.2 Medidas relevantes (Anexo II RD 311/2022)

Selección no exhaustiva de medidas de la categoría Alta implementadas:

- **op.acc.2** Identificación: federación con Cl@ve, MFA para administradores.
- **op.acc.6** Mecanismo de autenticación: WebAuthn / FIDO2 para personal interno.
- **op.exp.5** Gestión de cambios: pipeline GitOps con aprobación dual.
- **op.exp.8** Registro de actividad: append-only + hash encadenado.
- **op.exp.9** Registro de gestión de incidentes: integración con CSIRT CCN-CERT.
- **op.ext.4** Interconexión: canales TLS 1.3 + IPsec entre sistemas.
- **op.mon.3** Vigilancia: SIEM con correlación 24x7.
- **mp.com.4** Segregación de redes: micro-segmentación zero-trust.
- **mp.if.1** Áreas separadas: zonas de exposición, aplicación, datos y gestión separadas.
- **mp.s.2** Protección de servicios web: WAF certificado y revisión periódica.
- **mp.sw.1** Desarrollo seguro: SDL completo, SBOM, escaneo SAST/DAST.

### 6.4.3 Auditoría

- **Auditoría bienal obligatoria** por entidad certificadora acreditada.
- Plan de continuidad ITIL + BIA + simulacro semestral.
- Cuadro de mando de cumplimiento ENS publicado en la sede electrónica.

## 6.5 Arquitectura de seguridad zero-trust

```
┌── Identidad ──────────────────────────────────────────────────┐
│ Cl@ve · WebAuthn · OIDC interno · Vault                       │
└─────────────┬─────────────────────────────────────────────────┘
              │
┌── Política ─▼─────────────────────────────────────────────────┐
│ OPA (Open Policy Agent) · NetworkPolicies · mTLS              │
└─────────────┬─────────────────────────────────────────────────┘
              │
┌── Detección ▼─────────────────────────────────────────────────┐
│ Wazuh SIEM · Suricata IDS · Falco (runtime) · CCN-CERT feed   │
└─────────────┬─────────────────────────────────────────────────┘
              │
┌── Respuesta ▼─────────────────────────────────────────────────┐
│ SOAR (Shuffle) · Playbooks · Bastión · Quarantine network     │
└───────────────────────────────────────────────────────────────┘
```

## 6.6 Riesgos específicos de IA y mitigación

| Riesgo | Mitigación |
|---|---|
| **Prompt injection** (directa o indirecta vía documentos) | Sanitización, Llama Guard 3, política de "trust boundary" entre contenido del usuario y del corpus, salida estructurada (JSON) cuando aplique |
| **Jailbreak / desinhibición del modelo** | Guardrails de salida + reglas duras en orquestador + monitorización de patrones conocidos |
| **Data poisoning** del corpus | Firmas digitales en la ingesta, control de versiones, revisión humana de cambios sensibles |
| **Model extraction** | Rate-limit agresivo + watermark de salidas |
| **Sesgo y discriminación** | Auditoría algorítmica con DiscrIA + golden set diverso + métricas de equidad |
| **Alucinaciones** | RAG estricto + verificación con LLM-as-judge + umbrales de confianza |
| **Fuga de PII a través de logs** | Redacción automática (Presidio + regex) antes de persistir |
| **Modelo desactualizado** | Pipeline de re-evaluación trimestral; alerta si drift > 10 % |
| **Disponibilidad bajo ataque DDoS** | WAF + scrubbing + plan de modo degradado (respuestas pre-cacheadas) |
| **Manipulación de embeddings** | Firma criptográfica del índice + verificación antes de cargar |

## 6.7 Gobernanza algorítmica

### 6.7.1 Comité de Gobernanza Algorítmica Municipal

Composición:

- Concejal/a responsable del área digital (presidencia).
- Director/a TIC.
- Delegado/a de Protección de Datos.
- Responsable de Atención Ciudadana.
- Asesor/a jurídico/a.
- Responsable de Accesibilidad.
- Representante ciudadano/a (sociedad civil).
- Representante sindical.
- Asesor/a externo independiente (académico o de organización sin ánimo de lucro).

Funciones: aprobar políticas, revisar auditorías, recibir incidencias significativas, autorizar nuevas funcionalidades.

### 6.7.2 Transparencia pública

Publicación en la sede electrónica de:

- Descripción del sistema (no técnica, lenguaje ciudadano).
- Resumen de la DPIA y la FRIA.
- KPIs de calidad y equidad (CSAT, tasa de resolución, métricas por colectivo).
- Canal específico para reclamaciones algorítmicas.
- Informe anual de funcionamiento.

## 6.8 Anonimización y minimización

- **Detección automática** de DNI, NIE, IBAN, números de teléfono, correos electrónicos, matrículas y direcciones en cada turno con **Microsoft Presidio** + reglas personalizadas. La detección ocurre **en memoria** antes de cualquier persistencia.
- **Sustitución** por etiquetas (`[DNI]`, `[DIRECCIÓN]`) en logs.
- **K-anonimato k≥5** y **l-diversidad** en métricas agregadas.
- **Differential privacy** (ε≤2) en estadísticas publicadas.

## 6.9 Continuidad de negocio

| Concepto | Valor |
|---|---|
| RTO (Recovery Time Objective) | 4 h |
| RPO (Recovery Point Objective) | 15 min |
| Modo degradado | Respuestas pre-cacheadas top-1000 FAQs |
| Plan de contingencia | Redireccionamiento a 010 + chat humano + FAQ estática |
| Simulacro | Semestral, con reporte público |
| Backups | 3-2-1: tres copias, dos medios, una off-site cifrada |

## 6.10 Resumen del cumplimiento

| Norma | Estado objetivo antes de producción |
|---|---|
| ENS Alto | Certificado por entidad acreditada |
| RGPD | DPIA aprobada por DPD + registro de actividad publicado |
| AI Act | FRIA + inscripción en base de datos UE + marcado CE |
| EN 301 549 / WCAG 2.2 AA | Auditoría externa con sello AENOR / IRTI |
| ISO 27001/27701/42001 | En curso (objetivo año 2) |
| Accesibilidad Real Decreto 1112/2018 | Declaración de accesibilidad publicada |
