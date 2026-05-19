# Modelos seleccionados

## Principal

### Gemma 4 26B A4B Instruct

Se usa como modelo principal de redaccion porque en este equipo ya esta disponible dentro de `LM Studio`, tiene formato `MLX`, soporte de vision y capacidad de tool use, con una huella razonable para Apple Silicon.

## Embeddings

### Nomic Embed Text v1.5

Se usa para la capa semantica del RAG porque ya esta disponible localmente y su coste de carga es muy bajo.

## Fallback distribuido

### Qwen3.5 9B

Se recomienda para los Mac mini cuando quieras escalar el chatbot a toda la LAN con menor consumo por nodo.

## Criterio practico

- Calidad de respuesta y redaccion: `Gemma 4 26B`
- Throughput distribuido: `Qwen3.5 9B`
- RAG semantico ligero: `Nomic Embed Text v1.5`
