#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VISIBILITY_SOURCE="${VISIBILITY_SOURCE:-${1:-}}"
COMMERCE_SOURCE="${COMMERCE_SOURCE:-${2:-}}"
WORKFLOW_SOURCE="${WORKFLOW_SOURCE:-${3:-}}"
LARAVEL_SOURCE="${LARAVEL_SOURCE:-${4:-}}"
EMAIL_MARKETING_SOURCE="${EMAIL_MARKETING_SOURCE:-${5:-}}"

if [[ -z "$VISIBILITY_SOURCE" || -z "$COMMERCE_SOURCE" || -z "$WORKFLOW_SOURCE" || -z "$LARAVEL_SOURCE" || -z "$EMAIL_MARKETING_SOURCE" ]]; then
  cat >&2 <<'USAGE'
Usage:
  scripts/sync-from-source.sh <ai-visibility-skills> <agentic-commerce-skills> <ai-engineering-workflow-skills> <php-laravel-filament-skills> <email-marketing-skills>

or set:
  VISIBILITY_SOURCE=<path> COMMERCE_SOURCE=<path> WORKFLOW_SOURCE=<path> LARAVEL_SOURCE=<path> EMAIL_MARKETING_SOURCE=<path> scripts/sync-from-source.sh
USAGE
  exit 2
fi

rm -rf "$ROOT/skills/ai-visibility" "$ROOT/skills/agentic-commerce" "$ROOT/skills/engineering" "$ROOT/skills/productivity" "$ROOT/skills/product" "$ROOT/skills/filament" "$ROOT/skills/laravel" "$ROOT/skills/php" "$ROOT/skills/email-marketing"
cp -R "$VISIBILITY_SOURCE/skills/ai-visibility" "$ROOT/skills/"
cp -R "$COMMERCE_SOURCE/skills/agentic-commerce" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/engineering" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/productivity" "$ROOT/skills/"
cp -R "$WORKFLOW_SOURCE/skills/product" "$ROOT/skills/"
cp -R "$LARAVEL_SOURCE/skills/filament" "$ROOT/skills/"
cp -R "$LARAVEL_SOURCE/skills/laravel" "$ROOT/skills/"
cp -R "$LARAVEL_SOURCE/skills/php" "$ROOT/skills/"
mkdir -p "$ROOT/skills/email-marketing"
cp -R "$EMAIL_MARKETING_SOURCE/skills/." "$ROOT/skills/email-marketing/"

python3 "$ROOT/scripts/sync-plugin-manifest.py"
python3 "$ROOT/scripts/validate-plugin.py"
