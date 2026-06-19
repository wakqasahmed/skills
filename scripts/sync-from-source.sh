#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VISIBILITY_SOURCE="${1:-/opt/OSS-contributions/ai-visibility-skills}"
COMMERCE_SOURCE="${2:-/opt/OSS-contributions/agentic-commerce-skills}"
WORKFLOW_SOURCE="${3:-/opt/OSS-contributions/ai-engineering-workflow-skills}"

rm -rf "$ROOT/skills/ai-visibility" "$ROOT/skills/agentic-commerce" "$ROOT/skills/engineering-workflow"
cp -R "$VISIBILITY_SOURCE/skills/ai-visibility" "$ROOT/skills/"
cp -R "$COMMERCE_SOURCE/skills/agentic-commerce" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/engineering-workflow" "$ROOT/skills/"

python3 "$ROOT/scripts/validate-plugin.py"
