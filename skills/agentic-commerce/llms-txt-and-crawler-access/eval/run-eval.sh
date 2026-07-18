#!/usr/bin/env bash
set -euo pipefail

EVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(mktemp -d)"
trap 'rm -rf "$WORKSPACE"' EXIT
mkdir -p "$WORKSPACE/eval" "$WORKSPACE/home"
cp "$EVAL_DIR/check-contract.py" "$EVAL_DIR/held-out-cases.json" "$WORKSPACE/eval/"
cp "$EVAL_DIR/../SKILL.md" "$WORKSPACE/SKILL.md"
cat > "$WORKSPACE/sitecustomize.py" <<'PY'
import socket
import http.client
import urllib.request

def blocked(*args, **kwargs):
    raise OSError("network disabled for deterministic eval")

socket.socket = blocked
socket.create_connection = blocked
urllib.request.urlopen = blocked
http.client.HTTPConnection.connect = blocked
http.client.HTTPSConnection.connect = blocked
PY
PYTHONPATH="$WORKSPACE" HOME="$WORKSPACE/home" PYTHONNOUSERSITE=1 \
  python3 -s "$WORKSPACE/eval/check-contract.py"
