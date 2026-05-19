#!/usr/bin/env bash
set -euo pipefail

MODEL_LIST="${MODEL_LIST:-qwen3.5:9b}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama no esta instalado. Instala /Applications/Ollama.app o el binario en /usr/local/bin/ollama."
  exit 1
fi

"$(cd "$(dirname "$0")" && pwd)/install_ollama_launch_agent.sh"

for model in ${MODEL_LIST}; do
  echo "Descargando modelo ${model}..."
  ollama pull "${model}"
done

echo "Estado actual:"
curl -sf http://127.0.0.1:11434/api/tags | head -c 400 || true
echo
