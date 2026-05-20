#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

cd "${ROOT_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
pip install -e '.[dev]'

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
fi

mkdir -p \
  "${ROOT_DIR}/data/speech_temp" \
  "${ROOT_DIR}/data/whisper_models" \
  "${ROOT_DIR}/data/document_intake" \
  "${ROOT_DIR}/data/ocr_outputs" \
  "${ROOT_DIR}/data/demo_backend"

echo "Bootstrap complete."
echo "Next steps:"
echo "  1. Review .env"
echo "  2. Start the API with: source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  3. Open http://localhost:8000/static/demo.html"
