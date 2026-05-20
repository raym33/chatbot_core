#!/usr/bin/env bash
set -euo pipefail

KEY_PATH="${1:-$HOME/.ssh/chatbot_core_cluster_ed25519}"

mkdir -p "$(dirname "$KEY_PATH")"
chmod 700 "$(dirname "$KEY_PATH")"

if [[ -f "$KEY_PATH" ]]; then
  echo "Key already exists at $KEY_PATH"
else
  ssh-keygen -t ed25519 -N "" -f "$KEY_PATH" -C "chatbot-core-cluster"
fi

echo
echo "Public key:"
cat "${KEY_PATH}.pub"
