# Frameworks de inferencia

## Tabla comparativa

| Framework | Mejor para | Hardware objetivo | Ventajas | Limitaciones |
|---|---|---|---|---|
| LM Studio | Desarrollo, demos, Mac local, operadores no expertos | Apple Silicon, PC local | UI, API OpenAI-compatible, carga facil de modelos | No es el mejor para HA ni throughput masivo |
| Ollama | Nodos sencillos, edge, Mac mini, Linux pequeño | Apple Silicon, CPU/GPU local | Instalacion simple, API clara, buen fallback | Menos control fino de batching que vLLM |
| MLX-LM | Apple Silicon avanzado, fine-tuning LoRA local | Mac Studio, Mac mini, MacBook Pro | MLX nativo, LoRA, cuantizacion, prompt caching | Requiere mas trabajo de serving |
| llama.cpp | CPU/edge/embebido, GGUF, bajo coste | CPU, Apple, CUDA, Metal | Portabilidad extrema | Operacion a escala requiere envoltorio |
| vLLM | Produccion cloud/on-prem con GPUs NVIDIA/AMD | L40S, A100, H100, H200, B200 | PagedAttention, continuous batching, OpenAI API | Requiere servidores GPU y MLOps |
| SGLang | Agentes, RAG pesado, serving avanzado | GPUs datacenter | Buen rendimiento en workloads complejos | Menos universal que vLLM |
| TensorRT-LLM | Maximo rendimiento NVIDIA | H100, H200, B200 | Optimizacion profunda NVIDIA | Mas complejo de construir y operar |

## Recomendacion por fase

| Fase | Stack recomendado |
|---|---|
| Desarrollo local | LM Studio + Gemma/Qwen + Nomic embeddings |
| Piloto con 5 Macs | LM Studio en gateway + Ollama/MLX-LM en minis |
| Produccion media | vLLM con L40S/H100 + PostgreSQL + Redis + observabilidad |
| Produccion nacional | vLLM/SGLang/TensorRT-LLM en cluster GPU multi-zona |
