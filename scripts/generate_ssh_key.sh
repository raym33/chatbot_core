#!/usr/bin/env bash
set -euo pipefail

KEY_PATH="${1:-$HOME/.ssh/munibot_cluster_ed25519}"

mkdir -p "$(dirname "$KEY_PATH")"
chmod 700 "$(dirname "$KEY_PATH")"

if [[ -f "$KEY_PATH" ]]; then
  echo "La clave ya existe en $KEY_PATH"
else
  ssh-keygen -t ed25519 -N "" -f "$KEY_PATH" -C "munibot-cluster"
fi

echo
echo "Clave publica:"
cat "${KEY_PATH}.pub"
