#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE="${ROOT_DIR}/deploy/com.munibot.ollama.plist.template"
TARGET="${HOME}/Library/LaunchAgents/com.munibot.ollama.plist"

mkdir -p "${HOME}/Library/LaunchAgents"
sed "s#__HOME__#${HOME}#g" "${TEMPLATE}" > "${TARGET}"

launchctl unload "${TARGET}" >/dev/null 2>&1 || true
launchctl load -w "${TARGET}"

echo "LaunchAgent instalado en ${TARGET}"
