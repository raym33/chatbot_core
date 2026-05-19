# 5. HARDWARE E INFRAESTRUCTURA ON-PREMISE

## 5.1 Premisas de dimensionamiento

Asumimos los siguientes parámetros para el cálculo de capacidad:

| Parámetro | Valor |
|---|---|
| Población | 1.000.000 habitantes |
| Usuarios potenciales (>16 años) | 820.000 |
| Sesiones / mes en régimen | 1.000.000 |
| Mensajes / mes | 4.800.000 |
| Mensajes / segundo en pico | 18-22 |
| Tokens entrada media | 1.200 |
| Tokens salida media | 280 |
| Tokens totales / segundo en pico | ≈ 30.000-35.000 |
| Modelo principal | Salamandra-7B-Instruct (FP8) |
| Modelo refuerzo (10 % tráfico) | Llama 4 Scout (FP8, TP=2) |

Para soportar el pico con margen de seguridad del 40 % y la replicación activo-activo, el dimensionamiento total objetivo es **≈ 50.000 tokens/s sostenido por CPD**.

## 5.2 Elección de GPU

### 5.2.1 Comparativa de alternativas

| GPU | VRAM | Mem. BW | Coste (€) | Tok/s Llama 70B FP8 | Notas |
|---|---|---|---|---|---|
| NVIDIA H100 SXM | 80 GB HBM3 | 3,35 TB/s | 27.000-35.000 | 3.000 | Anterior generación, abundante en mercado |
| **NVIDIA H200 SXM** | **141 GB HBM3e** | **4,8 TB/s** | **31.000-40.000** | **6.500** | **Equilibrio capacidad / disponibilidad** |
| NVIDIA B200 SXM | 180 GB HBM3e | 8,0 TB/s | 45.000-55.000 | 17.500 | Líder absoluto en 2026 |
| AMD MI300X | 192 GB HBM3 | 5,3 TB/s | 18.000-25.000 | 4.800 | Alternativa europea-friendly, ROCm |
| AMD MI325X | 256 GB HBM3e | 6,0 TB/s | 22.000-30.000 | 6.200 | Mejor relación €/VRAM |

### 5.2.2 Recomendación

**Opción A (recomendada): NVIDIA H200**, por su equilibrio entre coste, disponibilidad en el canal europeo y madurez del ecosistema software (vLLM, SGLang, FlashAttention 3, TensorRT-LLM). 141 GB de VRAM permiten alojar holgadamente Salamandra-7B + Llama 4 Scout + Guard + embeddings en una sola GPU con MIG.

**Opción B (futuro-prueba): NVIDIA B200**, recomendada solo si el presupuesto y la disponibilidad del canal lo permiten. Reduce el número de GPUs necesarias por 2,5x y proyecta menor coste energético por token.

**Opción C (soberanía europea): AMD MI300X / MI325X**, valorable si se prioriza la diversificación frente a NVIDIA, aceptando un ecosistema software algo más inmaduro (ROCm 6.3+).

Para el resto del documento se asume la **Opción A (H200)** como configuración base.

## 5.3 Servidor de inferencia

### 5.3.1 Especificación de un nodo GPU
- **Chasis**: Supermicro SYS-821GE-TNHR / Dell PowerEdge XE9680 / HPE Cray XD675.
- **GPUs**: 8 × NVIDIA H200 SXM5 141 GB (interconectadas NVLink 4 + NVSwitch).
- **CPU**: 2 × Intel Xeon Platinum 8568Y (48 cores c/u, 96 cores totales).
- **RAM**: 2 TB DDR5 4800 MHz ECC RDIMM.
- **Almacenamiento local**: 4 × 7,68 TB NVMe Gen5 U.2 (30,7 TB usables) para modelos y caché.
- **Red**: 8 × 400 GbE InfiniBand NDR (un puerto por GPU) + 2 × 100 GbE Ethernet de gestión.
- **PSU**: 6 × 3.000 W redundancia N+N.
- **Consumo eléctrico nominal**: ≈ 10,2 kW por nodo.

### 5.3.2 Cantidad de nodos

**Capacidad por nodo H200 (8 GPUs)**:
- Salamandra-7B FP8 con batch 64 → ≈ 28.000 tokens/s
- Speculative decoding (factor 1,7×) → ≈ 47.000 tokens/s efectivos
- Restando overhead de Guard + RAG + clasificador → **≈ 38.000 tokens/s útiles**

**Necesidad por CPD**:
- Régimen pico: 35.000 tok/s
- Margen seguridad 40 %: 49.000 tok/s
- → **2 nodos GPU por CPD** (uno activo, uno hot-standby con tráfico de pre-producción y picos)

**Total**: **4 nodos GPU** = 32 H200 = 4,5 TB VRAM agregada.

### 5.3.3 GPUs para inferencia auxiliar
Para clasificador, embeddings, reranker y guardrails se utilizan **2 servidores adicionales** por CPD con GPUs más modestas:

- 2 × **NVIDIA L40S** (48 GB) por servidor, total 4 L40S por CPD.
- Coste por L40S: ≈ 8.500 €.
- Suficientes para 60.000 embeddings/s y 12.000 rerankings/s.

## 5.4 Almacenamiento

### 5.4.1 Almacenamiento principal (datos calientes)
- **Sistema**: NetApp AFF C400 / Pure Storage FlashArray //X / Dell PowerStore.
- **Capacidad**: 200 TB efectivos (NVMe TLC), expandible a 800 TB.
- **Protocolo**: NFS v4.1 + S3 nativo.
- **Réplica**: SnapMirror / asyncRep entre CPDs.

### 5.4.2 Object storage (corpus, modelos, logs)
- **MinIO** cluster (4 nodos x 24 discos x 16 TB SAS = 1,5 PB raw, 1,0 PB usable con EC 8+4).
- Bucket lifecycle: hot 90 días, warm 12 meses, frozen 5 años.

### 5.4.3 Bases de datos
- **PostgreSQL 17** (Patroni HA, 3 nodos x 32 cores, 256 GB RAM, 8 TB NVMe).
- **Milvus 2.5** (vector store distribuido, 4 nodos query + 2 nodos data, 2 TB RAM agregada).
- **OpenSearch 2.x** (3 nodos master + 6 data, 1 TB NVMe c/u).
- **Redis 7.4** (cluster 6 nodos, 256 GB RAM agregada, persistencia AOF).
- **Kafka 4** (3 brokers KRaft, 512 GB SSD c/u).

## 5.5 Red

- **Núcleo del CPD**: 2 switches spine 51,2 Tbps (Arista 7060X6 o similar).
- **Acceso**: 4 switches leaf 100 GbE.
- **InfiniBand NDR** dedicada para tráfico GPU↔GPU y GPU↔storage.
- **Doble salida WAN**: 2 × 10 Gbps simétricos con operadores distintos + DDoS scrubbing.
- **Microsegmentación** por NSX-T o Cilium NetworkPolicy.
- **DNS interno** con vistas: ningún FQDN del backend del chatbot resuelve desde internet.

## 5.6 CPD: dos zonas geográficamente separadas

| Característica | CPD principal | CPD secundario |
|---|---|---|
| Ubicación | Edificio municipal certificado | Proveedor ENS-Alto (p.ej. AYESA, Telefónica Tech, Cellnex) |
| Distancia mínima | — | > 40 km con caminos físicos diversos |
| Certificación | ENS-Alto, ISO 27001, EN 50600 Tier III | Igual |
| Energía | Doble acometida + UPS + generador 72 h | Idem |
| Refrigeración | DLC (Direct Liquid Cooling) para GPUs | Idem |
| PUE objetivo | ≤ 1,3 | ≤ 1,3 |
| Personal 24×7 | Sí (subcontratado o municipal) | Sí |

## 5.7 Tabla resumen de hardware por CPD

| Componente | Modelo / spec | Unidades | Coste unitario (€) | Total (€) |
|---|---|---|---|---|
| Servidor GPU 8×H200 | Supermicro SYS-821GE-TNHR | 2 | 285.000 | 570.000 |
| Servidor GPU aux 2×L40S | Supermicro AS-2125HS-TNR | 2 | 38.000 | 76.000 |
| Servidor de propósito general (Kubernetes worker) | Dell R760, 2×Xeon, 1 TB RAM | 6 | 18.000 | 108.000 |
| Cabina almacenamiento NVMe 200 TB | NetApp AFF C400 | 1 | 180.000 | 180.000 |
| Nodos MinIO | Dell R760xd, 24×16TB SAS | 4 | 28.000 | 112.000 |
| Switches core + leaf 400 GbE | Arista 7060X6/7050X4 | 6 | 42.000 | 252.000 |
| Switches gestión 25 GbE | Arista 7280 | 2 | 12.000 | 24.000 |
| Firewall NGFW | Palo Alto PA-5450 | 2 | 65.000 | 130.000 |
| WAF dedicado | F5 ASM (o ModSecurity en HW) | 2 | 18.000 | 36.000 |
| Balanceador L4/L7 | Citrix ADC / HAProxy Enterprise | 2 | 14.000 | 28.000 |
| Rack 47U + PDU + cableado | — | 4 | 6.500 | 26.000 |
| HSM (módulo de seguridad hardware) | nCipher nShield XC | 2 | 22.000 | 44.000 |
| UPS modular 80 kVA | Eaton 93PM | 1 | 28.000 | 28.000 |
| Sistema de monitorización OOB | Lenovo XClarity / iDRAC | — | 8.000 | 8.000 |
| **Subtotal hardware por CPD** | | | | **1.622.000** |

**Total dos CPDs**: ≈ **3.244.000 €** en hardware bruto. Con la consolidación del CPD secundario contratado como servicio (no compra) o con sinergia con infra municipal preexistente, el coste imputable al proyecto se ajusta en la sección de costes (capítulo 8).

## 5.8 Software de plataforma (open source)

| Capa | Software | Licencia |
|---|---|---|
| Sistema operativo | Rocky Linux 9 / Ubuntu 24.04 LTS | GPLv2 / Free |
| Orquestador | Kubernetes 1.32 / RKE2 / OpenShift OKD | Apache 2.0 |
| Service mesh | Istio o Linkerd | Apache 2.0 |
| Container runtime | containerd + NVIDIA Container Toolkit | Apache 2.0 |
| Almacenamiento K8s | Longhorn + Rook (Ceph) | Apache 2.0 |
| Secretos | HashiCorp Vault (OSS) | MPL 2.0 |
| CI/CD | Forgejo + Drone + ArgoCD | MIT/Apache |
| Observabilidad | Prometheus + Grafana + Loki + Tempo + OTel | Apache 2.0 |
| SIEM | Wazuh | GPLv2 |
| Backup | Restic + Velero | BSD / Apache |
| Configuración | Ansible | GPLv3 |

## 5.9 Plan de capacidad y escalado

| Año | Tráfico esperado | Nodos GPU activos | Acción |
|---|---|---|---|
| 1 (piloto) | 0,3M msg/mes | 2 (1 por CPD) | Configuración inicial |
| 2 | 1,7M msg/mes | 3 | +1 nodo GPU CPD principal |
| 3 | 4,8M msg/mes | 4 | Plena capacidad descrita |
| 4 | 6,5M msg/mes | 4-5 | Evaluar refresh a B300 o MI400X |
| 5 | 8M msg/mes | 5-6 | Refresco completo de modelos y plataforma |

## 5.10 Sostenibilidad y consumo energético

- **Consumo agregado por CPD**: ≈ 32-38 kW pico, ≈ 22 kW promedio.
- **Coste eléctrico anual**: 22 kW × 8.760 h × 0,16 €/kWh × 1,3 (PUE) = **40.000 €/CPD/año**.
- **Refrigeración líquida directa (DLC)** reduce un 35-40 % el consumo de climatización frente a aire forzado.
- **Auditoría de huella de carbono** anual con metodología GHG Protocol Scope 1-3.
- **Compensación**: contrato PPA con generación renovable certificada (objetivo 100 % renovable en año 2).

## 5.11 Resumen ejecutivo del dimensionamiento

| Concepto | Cantidad |
|---|---|
| GPUs H200 totales | 32 (16 por CPD) |
| GPUs L40S totales | 8 (4 por CPD) |
| Servidores GPU principales | 4 |
| Servidores auxiliares | 16 |
| VRAM agregada | 5,0 TB |
| Almacenamiento NVMe rápido | 400 TB (200/CPD) |
| Almacenamiento de objetos | 2,0 PB |
| Capacidad sostenida | ≈ 50.000 tokens/s por CPD |
| Concurrencia soportada | > 1.200 sesiones simultáneas |
| Disponibilidad nominal | 99,95 % (con CPD secundario activo) |
