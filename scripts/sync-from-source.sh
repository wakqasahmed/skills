#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VISIBILITY_SOURCE="${VISIBILITY_SOURCE:-${1:-}}"
COMMERCE_SOURCE="${COMMERCE_SOURCE:-${2:-}}"
WORKFLOW_SOURCE="${WORKFLOW_SOURCE:-${3:-}}"

if [[ -z "$VISIBILITY_SOURCE" || -z "$COMMERCE_SOURCE" || -z "$WORKFLOW_SOURCE" ]]; then
  cat >&2 <<'USAGE'
Usage:
  scripts/sync-from-source.sh <ai-visibility-skills> <agentic-commerce-skills> <ai-engineering-workflow-skills>

or set:
  VISIBILITY_SOURCE=<path> COMMERCE_SOURCE=<path> WORKFLOW_SOURCE=<path> scripts/sync-from-source.sh
USAGE
  exit 2
fi

rm -rf "$ROOT/skills/ai-visibility" "$ROOT/skills/agentic-commerce" "$ROOT/skills/engineering" "$ROOT/skills/productivity" "$ROOT/skills/product"
cp -R "$VISIBILITY_SOURCE/skills/ai-visibility" "$ROOT/skills/"
cp -R "$COMMERCE_SOURCE/skills/agentic-commerce" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/engineering" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/productivity" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/product" "$ROOT/skills/"

python3 "$ROOT/scripts/sync-plugin-manifest.py"
python3 "$ROOT/scripts/validate-plugin.py"
