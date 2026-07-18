#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/skills/ai-visibility/ai-visibility-audit/eval/run_eval.py"
bash "$ROOT/skills/engineering/clarify-work/eval/run-eval.sh"
bash "$ROOT/skills/engineering/subagent-pipeline/eval/run-eval.sh" --dry-run
bash "$ROOT/skills/engineering/to-prd/eval/run-eval.sh"
bash "$ROOT/skills/email-marketing/eval/run-eval.sh"
