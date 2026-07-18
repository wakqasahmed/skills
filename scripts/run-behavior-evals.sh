#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/skills/ai-visibility/ai-visibility-audit/eval/run_eval.py"
bash "$ROOT/skills/engineering/clarify-work/eval/run-eval.sh"
bash "$ROOT/skills/engineering/subagent-pipeline/eval/run-eval.sh" --dry-run
bash "$ROOT/skills/engineering/to-prd/eval/run-eval.sh"
python3 "$ROOT/skills/agentic-commerce/commerce-protocol-readiness/eval/run.py"
bash "$ROOT/skills/agentic-commerce/agent-readiness/eval/run-eval.sh"
python3 "$ROOT/skills/agentic-commerce/ecommerce-policy-readiness/eval/run.py"
bash "$ROOT/skills/agentic-commerce/llms-txt-and-crawler-access/eval/run-eval.sh"
bash "$ROOT/skills/email-marketing/eval/run-eval.sh"
bash "$ROOT/skills/email-marketing/00-email-marketing-guardrails/eval/run-eval.sh"
