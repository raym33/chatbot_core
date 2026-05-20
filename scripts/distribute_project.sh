#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 user host1 [host2 ...]"
  exit 1
fi

USER_NAME="$1"
shift
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

for HOST in "$@"; do
  echo "Syncing ${HOST}..."
  rsync -az --delete \
    --exclude ".venv" \
    --exclude "__pycache__" \
    --exclude ".pytest_cache" \
    "${PROJECT_DIR}/" "${USER_NAME}@${HOST}:~/chatbot_core/"
done
