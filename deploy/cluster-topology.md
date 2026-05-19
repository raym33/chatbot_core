# Topologia recomendada del cluster

## Roles

| Equipo | IP prevista | Rol |
|---|---|---|
| MacBook | `192.168.100.1` | Gateway FastAPI, widget web, persistencia SQLite, coordinacion |
| mini1 | `192.168.100.50` | Inferencia principal de chat |
| mini2 | `192.168.100.51` | Inferencia secundaria de chat |
| mini3 | `192.168.100.2` | Nodo de razonamiento pesado o futura vision |
| mini4 | `192.168.100.3` | Respaldo y actualizaciones canary |

## Modelos recomendados

| Uso | Modelo |
|---|---|
| Chat principal | `qwen3.5:9b` |
| Consultas mas complejas | `qwen3:30b` |
| Embeddings recomendados | `qwen3-embedding:4b` |
| Embeddings ligeros | `bge-m3` |
| Vision opcional | `gemma3:12b` |

## Criterio operativo

- Todos los nodos de atencion ciudadana deben ser homogeneos en comportamiento.
- El `MacBook` no debe cargar modelos pesados si actua como gateway.
- `mini1` y `mini2` deben servir el mismo modelo para balanceo simple y predecible.
- `mini3` puede reservarse para consultas de baja frecuencia y alta complejidad.
- `mini4` conviene dejarlo como respaldo o banco de pruebas, no como nodo critico desde el dia uno.
