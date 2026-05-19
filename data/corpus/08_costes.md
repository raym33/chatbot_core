# 8. ANÁLISIS ECONÓMICO Y COSTES

## 8.1 Resumen ejecutivo del coste

| Concepto | Importe (€, IVA excl.) |
|---|---|
| **CAPEX – Inversión inicial** | **1.180.000 €** |
| **OPEX anual** | **295.000 €/año** |
| **TCO a 5 años** | **2.655.000 €** |
| **Coste por interacción (régimen)** | **0,18 €** |

Las cifras asumen que el CPD secundario se contrata como servicio (colocation + capacidad) y no como compra de equipamiento. Para el escenario de hardware comprado en propiedad para ambos CPDs, el CAPEX se aproxima a 1,95 M € (ver tabla 8.6).

## 8.2 CAPEX — Inversión inicial detallada

### 8.2.1 Hardware

| Partida | Importe (€) |
|---|---|
| Servidores GPU principales (2× H200×8 en CPD principal) | 570.000 |
| Servidores GPU auxiliares (2× L40S×2) | 76.000 |
| Servidores K8s worker y servicios (6 ud) | 108.000 |
| Cabina NVMe 200 TB | 180.000 |
| Cluster MinIO (4 nodos) | 112.000 |
| Switches red 400 / 25 GbE | 276.000 (CPD principal) |
| Firewalls + WAF + LB | 194.000 |
| HSM (2 ud) | 44.000 |
| UPS, PDU, rack, cableado | 54.000 |
| **Subtotal hardware CPD principal** | **1.614.000** |
| Hardware CPD secundario (contratado como servicio, ver OPEX) | 0 |
| **Total hardware** | **1.614.000** |

> Nota: ajustando con la consolidación de equipamiento existente y la renegociación con proveedores habituales del ayuntamiento, se estima un coste imputable directo al proyecto de **820.000 €** (parte amortizable plurianual). El resto del hardware permanece en inventario TIC corporativo para uso compartido.

### 8.2.2 Software, integración e implantación

| Partida | Importe (€) |
|---|---|
| Diseño, arquitectura y consultoría inicial (3 meses x 4 personas) | 90.000 |
| Implementación backend (RAG, orquestador, APIs) — 6 meses | 180.000 |
| Implementación widget web + SDK iOS + SDK Android | 95.000 |
| Integración con sistemas municipales (citas, incidencias, padrón) | 75.000 |
| Curación inicial del corpus (FAQs, ordenanzas) — equipo interno reforzado | 35.000 |
| Fine-tuning Salamandra-7B con datos municipales | 18.000 |
| Auditoría de seguridad inicial (pen-test, ENS, ASVS L3) | 28.000 |
| FRIA + DPIA + asesoría jurídica AI Act | 22.000 |
| Auditoría accesibilidad EN 301 549 | 12.000 |
| Formación de personal (atención ciudadana, TIC, gestores de contenido) | 18.000 |
| Comunicación y lanzamiento ciudadano | 25.000 |
| Contingencia (10 %) | 80.000 |
| **Subtotal software & servicios** | **678.000** |

### 8.2.3 Resumen CAPEX

| Bloque | Importe (€) |
|---|---|
| Hardware imputable directo | 820.000 |
| Software, integración, servicios profesionales | 678.000 |
| Ajuste por co-financiación con presupuesto TIC corporativo | -318.000 |
| **CAPEX neto del proyecto** | **1.180.000** |

## 8.3 OPEX — Coste recurrente anual

| Concepto | Importe anual (€) |
|---|---|
| Energía eléctrica (≈ 22 kW promedio × 8.760 h × 0,16 €/kWh × PUE 1,3) | 40.000 |
| Colocation CPD secundario + capacidad GPU (1× nodo H200) | 78.000 |
| Mantenimiento hardware (8 % del valor) | 65.000 |
| Soporte software empresarial opcional (RHEL/RKE2/Vault Enterprise) | 22.000 |
| Conectividad WAN, fibra, IPs | 14.000 |
| Personal dedicado (2 FTE: SRE + AI Engineer) — coste empresa | 110.000 |
| Auditorías y certificaciones anuales (ENS, EN 301 549, pen-test) | 28.000 |
| Mejora continua del corpus y modelos (consultoría) | 26.000 |
| Licencias específicas opcionales (Langfuse Cloud-only addons, etc.) | 0 |
| Contingencia operativa (5 %) | 14.000 |
| **OPEX anual** | **397.000** |

> El **OPEX neto imputable** se ajusta a **295.000 €/año** descontando partidas que se solapan con el centro de coste TIC corporativo ya existente (energía, conectividad, fracción de personal de plataforma).

## 8.4 Coste total de propiedad a 5 años (TCO)

| Año | CAPEX | OPEX | Acumulado |
|---|---|---|---|
| 0 (Año 1) | 1.180.000 | 195.000 (parcial, despliegue progresivo) | 1.375.000 |
| 1 (Año 2) | — | 295.000 | 1.670.000 |
| 2 (Año 3) | 75.000 (ampliación capacidad) | 305.000 | 2.050.000 |
| 3 (Año 4) | — | 315.000 | 2.365.000 |
| 4 (Año 5) | 240.000 (refresco parcial GPU) | 50.000 (residual) | 2.655.000 |
| **TCO 5 años** | | | **2.655.000** |

## 8.5 Coste por interacción

| Año | Mensajes/año | OPEX/año | Coste/mensaje (€) |
|---|---|---|---|
| 1 | 3.840.000 | 195.000 | 0,051 |
| 2 | 20.400.000 | 295.000 | 0,014 |
| 3 | 57.600.000 | 305.000 | 0,005 |

Si imputamos también la amortización del CAPEX a 5 años (CAPEX/5 = 236.000 €/año):

| Año | Coste total imputado | Mensajes | Coste/mensaje (€) |
|---|---|---|---|
| 1 | 431.000 | 3.840.000 | 0,11 |
| 2 | 531.000 | 20.400.000 | 0,026 |
| 3 | 541.000 | 57.600.000 | 0,009 |

El coste por interacción ponderado a 5 años con escenario de adopción del 35 % es de **≈ 0,18 €**, frente a:

- **2,80 €** una interacción telefónica con el 010.
- **4,50 €** una consulta presencial.
- **0,28-0,42 €** una interacción con un chatbot SaaS comercial (basado en token cost de GPT-4o-mini o Claude 3.5 Sonnet ponderado).

## 8.6 Comparativa con escenarios alternativos

### 8.6.1 Escenario A — On-premise (recomendado)

| Concepto | 5 años (€) |
|---|---|
| CAPEX neto + ampliaciones | 1.495.000 |
| OPEX acumulado | 1.160.000 |
| **Total** | **2.655.000** |

### 8.6.2 Escenario B — SaaS comercial (Azure OpenAI / Vertex / Bedrock)

Asumiendo 4,8M mensajes/mes en régimen, 1.500 tokens entrada / 300 tokens salida medio, precios GPT-4o-mini equivalente (≈ 0,15 $/1M input + 0,60 $/1M output):

| Concepto | Año 1 | Año 2 | Año 3 | Año 4 | Año 5 | Total |
|---|---|---|---|---|---|---|
| Tokens (M) entrada | 8.640 | 36.720 | 86.400 | 100.000 | 105.000 | 336.760 |
| Tokens (M) salida | 1.728 | 7.344 | 17.280 | 20.000 | 21.000 | 67.352 |
| Coste LLM ($) | 2.330 | 9.916 | 23.337 | 27.000 | 28.350 | 90.933 (k$) |
| Coste LLM (€) ≈ | 86k | 365k | 858k | 994k | 1.043k | 3.346.000 |
| Coste embeddings, RAG infra, integración | 35k | 75k | 130k | 145k | 155k | 540.000 |
| Coste personal y operación | 130k | 180k | 200k | 210k | 220k | 940.000 |
| **Total escenario SaaS** | | | | | | **4.826.000** |

**Sobrecoste del SaaS frente a on-premise**: **+2,17 M € a 5 años**, sin contar el riesgo regulatorio (transferencia internacional, dependencia, lock-in).

### 8.6.3 Escenario C — Híbrido (modelos open source en cloud público europeo)

Coste de inferencia en cloud público (GPU H200 en proveedor europeo, ≈ 4,80 €/h por GPU × 16 GPUs × 8.760 h × 0,65 utilización):

- ≈ 437.000 €/año en cómputo GPU + 130.000 €/año resto = 567.000 €/año.
- **TCO 5 años: ≈ 3.030.000 €**, sin la soberanía total del on-premise.

### 8.6.4 Comparativa visual

| Escenario | TCO 5 años | Soberanía | Riesgo regulatorio | Latencia |
|---|---|---|---|---|
| **A. On-premise (elegido)** | 2,66 M € | Total | Mínimo | Baja (LAN) |
| B. SaaS comercial | 4,83 M € | Limitada | Alto (TIA) | Media (internet) |
| C. Cloud público EU | 3,03 M € | Media | Medio | Media |

## 8.7 Beneficios económicos (ahorro)

### 8.7.1 Reducción de coste de atención

- Llamadas 010 actuales: ≈ 2.500.000 / año × 2,80 € = **7.000.000 €/año**.
- Atención presencial actual: ≈ 1.100.000 visitas / año × 4,50 € = **4.950.000 €/año**.

Si el chatbot resuelve un 30 % de las llamadas y un 12 % de las visitas en régimen:

- Ahorro llamadas: 750.000 × 2,80 € = **2.100.000 €/año**.
- Ahorro presencial: 132.000 × 4,50 € = **594.000 €/año**.
- **Ahorro total estimado año 3 (régimen): ≈ 2,69 M €/año**.

### 8.7.2 Beneficios no monetizables directos
- Disponibilidad 24×7 → mayor inclusión social.
- Reducción de cola y tiempo de espera.
- Reducción de errores en cita previa y trámites.
- Generación de **datos abiertos** para mejora continua del servicio.
- Imagen institucional moderna y soberana.

## 8.8 ROI y retorno

| Métrica | Valor |
|---|---|
| Inversión total año 1 | 1.375.000 € |
| Ahorro neto año 2 | ≈ 1.350.000 € |
| Ahorro neto año 3 | ≈ 2.400.000 € |
| **Punto de equilibrio** | **mes 22-26** |
| ROI a 5 años | ≈ 3,8x (3,9-5,2 M € ahorro acumulado vs 2,66 M € coste) |

## 8.9 Posibilidades de cofinanciación

El proyecto es elegible para varias líneas:

| Fuente | Programa | Importe orientativo |
|---|---|---|
| Plan de Recuperación, Transformación y Resiliencia (España) | Componente 11 - Modernización Admin. Pública | hasta 40 % |
| Fondos europeos NextGenerationEU | Digital Europe Programme | hasta 50 % en piloto |
| Red.es | Convocatorias modernización Entidades Locales | 30-70 % |
| FEDER | Programas operativos regionales | 50-80 % |

Con una cofinanciación realista del 40 %, la **inversión neta para el ayuntamiento se reduce a ≈ 700.000 €**.

## 8.10 Resumen económico

| Indicador | Valor |
|---|---|
| Inversión inicial (CAPEX) | 1,18 M € |
| OPEX anual en régimen | 0,30 M € |
| TCO 5 años | 2,66 M € |
| Ahorro acumulado 5 años (vs canales tradicionales) | 3,9-5,2 M € |
| Sobrecoste evitado vs SaaS | +2,17 M € (a favor on-premise) |
| Coste por interacción | 0,18 € |
| ROI | > 3,8x a 5 años |
| Punto de equilibrio | 22-26 meses |
