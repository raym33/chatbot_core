# 9. ROADMAP, GESTIÓN DE RIESGOS Y KPIs

## 9.1 Fases del proyecto

Aunque este documento es un **estudio de viabilidad sin compromiso de plazos**, se propone una secuencia indicativa para orientar la planificación.

### Fase 0 — Preparación (meses 0-3)
- Aprobación política y consignación presupuestaria.
- Constitución del Comité de Gobernanza Algorítmica.
- DPIA preliminar y FRIA preliminar.
- Licitación o procedimiento de contratación.
- Catalogación inicial del corpus.

### Fase 1 — Piloto cerrado (meses 3-9)
- Despliegue de infraestructura mínima (1 nodo GPU en CPD principal).
- Implementación RAG sobre 800 FAQs validadas.
- Canal web exclusivamente, dirigido a 5.000 usuarios voluntarios.
- Métricas, observabilidad y ciclo de mejora semanal.
- Auditoría inicial de seguridad y accesibilidad.

### Fase 2 — Piloto abierto (meses 9-12)
- Apertura al público general en canal web.
- Lanzamiento app móvil (iOS y Android).
- Incorporación del módulo de **incidencias urbanas** (lectura+escritura).
- Integración con cita previa (lectura primero, reserva después).
- Plan de comunicación ciudadana.

### Fase 3 — Producción plena (meses 12-18)
- Cluster completo activo-activo dos CPDs.
- Cobertura completa de FAQs, citas e incidencias.
- Fine-tuning específico del municipio.
- Certificación ENS Alta formal.
- Registro UE de sistema de alto riesgo (AI Act).

### Fase 4 — Evolución (meses 18-36)
- Incorporación de trámites autenticados (Cl@ve).
- Lenguas cooficiales si aplica.
- Voz (canal telefónico 010 con IA conversacional).
- Multimodalidad (visión para incidencias por foto).
- Integración avanzada con servicios sociales y emergencias.

## 9.2 Diagrama de Gantt (alto nivel, indicativo)

```
Meses:          0   3   6   9   12  15  18  24  30  36
F0 Preparación  ████
F1 Piloto cerr.    ██████
F2 Piloto abie.          ████
F3 Producción              ███████
F4 Evolución                       ██████████████
```

## 9.3 Equipo necesario

### 9.3.1 Equipo del ayuntamiento
| Perfil | Dedicación | Fase |
|---|---|---|
| Sponsor (Concejalía Digital) | 5 % | Todas |
| Project Manager municipal | 50 % | Todas |
| Responsable funcional (Atención Ciudadana) | 40 % | Todas |
| Responsable TIC | 30 % | Todas |
| Delegado/a de Protección de Datos | 15 % | Todas |
| Arquitecto/a TIC | 50 % | F0-F3 |
| Curadores de contenido (Comunicación + Servicios) | 100 % × 3 personas | F0-F2 |
| SRE / DevOps | 100 % × 2 personas | F1+ |
| AI Engineer / MLOps | 100 % × 1 persona | F1+ |

### 9.3.2 Equipo externo (adjudicatario)
| Perfil | Dedicación |
|---|---|
| Arquitecto/a IA senior | 50 % |
| Ingenieros backend (RAG, orquestación) | 2 FTE |
| Ingeniero MLOps | 1 FTE |
| Ingenieros frontend (web + iOS + Android) | 1 + 1 + 1 FTE |
| Especialista en accesibilidad | 0,3 FTE |
| Especialista ciberseguridad ENS | 0,3 FTE |
| Lingüista computacional | 0,2 FTE |
| QA / Test | 1 FTE |

## 9.4 Hitos críticos

| Hito | Descripción | Fase |
|---|---|---|
| H1 | DPIA aprobada por DPD | F0 |
| H2 | Infraestructura piloto operativa | F1 |
| H3 | Validación funcional 800 FAQs (≥ 92 % precisión) | F1 |
| H4 | Aprobación FRIA y registro UE AI Act | F2 |
| H5 | Lanzamiento app móvil en stores | F2 |
| H6 | Certificación ENS Alta | F3 |
| H7 | Régimen pleno con 220k usuarios/mes | F3 |
| H8 | Auditoría algorítmica anual aprobada | F4 |

## 9.5 Matriz de riesgos

### 9.5.1 Riesgos técnicos

| ID | Riesgo | Prob. | Imp. | Estrategia |
|---|---|---|---|---|
| RT-01 | Alucinaciones del LLM en información oficial | Alta | Crítico | RAG estricto + LLM-as-judge + citado obligatorio + escalado humano |
| RT-02 | Latencia degradada en horas punta | Media | Alto | Autoescalado + speculative decoding + caché de prompts frecuentes |
| RT-03 | Caída del CPD principal | Baja | Crítico | Activo-activo + DRP < 4 h RTO |
| RT-04 | Indisponibilidad por ataque DDoS | Media | Alto | WAF + scrubbing + modo degradado pre-cacheado |
| RT-05 | Drift del modelo (calidad bajando con tiempo) | Media | Medio | Evaluación nocturna golden set + alerta drift > 5 % |
| RT-06 | Fallo masivo de hardware GPU | Baja | Alto | Redundancia + contrato 4-h on-site + GPU de respaldo en cold-spare |
| RT-07 | Bug en cliente móvil bloqueando uso | Media | Medio | Phased release + remote config + rollback < 1 h |
| RT-08 | Corpus desactualizado (ordenanzas cambiadas) | Alta | Alto | Pipeline ingesta diaria + alerta de cambios normativos |

### 9.5.2 Riesgos legales y regulatorios

| ID | Riesgo | Prob. | Imp. | Estrategia |
|---|---|---|---|---|
| RL-01 | Sanción por no inscripción AI Act | Baja | Crítico | Inscripción antes de producción + FRIA actualizada anual |
| RL-02 | Reclamación RGPD por mal manejo de datos | Media | Alto | DPIA + anonimización + auditorías + canal DPD claro |
| RL-03 | Reclamación de accesibilidad (RD 1112/2018) | Media | Medio | Auditoría anual + plan de mejora continua + declaración pública |
| RL-04 | Cambio de licencia de un modelo open source | Baja | Medio | Diversificación (Salamandra + Llama + Qwen) + plan de migración |
| RL-05 | No conformidad ENS en auditoría bienal | Baja | Alto | Plan de remediación continuo + SIEM 24x7 |

### 9.5.3 Riesgos sociales y reputacionales

| ID | Riesgo | Prob. | Imp. | Estrategia |
|---|---|---|---|---|
| RS-01 | Sesgo discriminatorio detectado (origen, género, edad) | Media | Crítico | DiscrIA + auditoría algorítmica + comité ético + golden set diverso |
| RS-02 | Brecha digital: colectivos vulnerables excluidos | Alta | Alto | Lectura fácil + sesiones presenciales asistidas + 010 humano nunca eliminado |
| RS-03 | Polémica mediática por error notorio | Media | Alto | Comunicación proactiva + transparencia + protocolo de crisis |
| RS-04 | Rechazo sindical por sustitución de personal | Media | Medio | Mensaje claro: complemento, no sustitución; formación |
| RS-05 | Pérdida de confianza tras incidente de seguridad | Baja | Crítico | Notificación inmediata + plan de recuperación + auditoría independiente |

### 9.5.4 Riesgos económicos

| ID | Riesgo | Prob. | Imp. | Estrategia |
|---|---|---|---|---|
| RE-01 | Sobrecoste por subida precio GPU | Media | Medio | Contratos plurianuales + diversificación NVIDIA/AMD |
| RE-02 | Adopción ciudadana inferior a la prevista | Media | Alto | Plan comunicación + iteración rápida + UX testing |
| RE-03 | Coste energético subiendo | Alta | Bajo | PPA renovable + eficiencia (FP8/INT4) |

## 9.6 KPIs y cuadro de mando

### 9.6.1 KPIs ciudadanía
| KPI | Objetivo año 1 | Objetivo régimen |
|---|---|---|
| Usuarios activos únicos/mes | 35.000 | 220.000 |
| Sesiones/usuario/mes | 1,8 | 3,5 |
| Tasa de resolución sin escalado | ≥ 65 % | ≥ 82 % |
| Tasa de derivación a humano efectiva | ≥ 90 % | ≥ 97 % |
| Tiempo medio de respuesta (TTFT) | ≤ 1,5 s | ≤ 1,0 s |
| Sesión media (mensajes/sesión) | 4,0 | 4,8 |
| Tareas completadas (cita reservada, incidencia creada) | ≥ 92 % | ≥ 98 % |

### 9.6.2 KPIs calidad
| KPI | Objetivo año 1 | Objetivo régimen |
|---|---|---|
| Precisión factual (auditada) | ≥ 92 % | ≥ 96 % |
| Tasa de alucinación detectada | < 4 % | < 1,5 % |
| CSAT (👍 sobre valoradas) | ≥ 78 % | ≥ 88 % |
| NPS | ≥ 25 | ≥ 50 |
| Cobertura del corpus sobre intenciones reales | ≥ 80 % | ≥ 95 % |

### 9.6.3 KPIs operativos y técnicos
| KPI | Objetivo |
|---|---|
| Disponibilidad mensual | ≥ 99,9 % |
| Latencia P95 respuesta completa | ≤ 4,0 s |
| Throughput sostenido | ≥ 30.000 tokens/s pico |
| Incidentes críticos al año | ≤ 2 |
| MTTR (Mean Time To Recovery) | < 30 min |
| Cobertura tests (CI) | ≥ 85 % |
| Vulnerabilidades críticas SAST/DAST abiertas | 0 |
| Tiempo medio de ingesta corpus → producción | ≤ 24 h |

### 9.6.4 KPIs equidad y accesibilidad
| KPI | Objetivo |
|---|---|
| Diferencia CSAT mayores 65 vs media | ≤ 4 pp |
| Diferencia CSAT colectivos vulnerables vs media | ≤ 4 pp |
| Cumplimiento WCAG 2.2 AA | 100 % criterios A+AA |
| Reclamaciones por accesibilidad/año | < 5 |

### 9.6.5 KPIs económicos
| KPI | Objetivo |
|---|---|
| Coste por interacción | ≤ 0,20 € (régimen) |
| Ahorro neto anual vs canales tradicionales | ≥ 1,5 M € (año 2), ≥ 2,5 M € (año 3) |
| Plazo de retorno | ≤ 26 meses |
| Desviación presupuestaria | ≤ 10 % anual |

## 9.7 Mecanismos de mejora continua

- **Retros quincenales** con todo el equipo.
- **Revisión mensual** del comité de gobernanza.
- **Informe trimestral público** de funcionamiento.
- **Auditoría algorítmica anual** independiente con publicación de resultados.
- **Canal específico** de reclamación algorítmica con respuesta motivada.
- **Hackathon ciudadano** anual con datos sintéticos para co-creación.

## 9.8 Criterios de éxito (go/no-go entre fases)

### Go a Fase 2 (piloto abierto)
- Precisión ≥ 90 %, alucinación < 5 %, CSAT ≥ 75 %.
- ENS Medio operativo.
- DPIA y FRIA aprobadas.
- Plan de comunicación validado.

### Go a Fase 3 (producción plena)
- 6 meses de piloto abierto sin incidentes críticos.
- KPIs de calidad sostenidos.
- Disponibilidad ≥ 99,5 %.
- Auditoría ENS Alta aprobada.

### Continuidad anual
- ROI proyectado positivo.
- KPIs de equidad cumplidos.
- No sanciones AOD/AEPD.
- Renovación apoyo comité de gobernanza.

## 9.9 Plan de salida y reversibilidad

Para evitar dependencia de proveedor:

- Toda la propiedad intelectual del corpus, prompts y configuración pertenece al ayuntamiento.
- Modelos en formato estándar (Safetensors) almacenados en MinIO municipal.
- Documentación técnica completa y actualizada (Anexo IV AI Act).
- Contrato con cláusula de transferencia de conocimiento a un nuevo adjudicatario o equipo interno.
- Posibilidad de **internalización completa** tras año 3 (equipo de 4-5 FTE).
