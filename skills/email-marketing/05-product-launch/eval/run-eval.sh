#!/usr/bin/env bash
set -euo pipefail

EVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$EVAL_DIR/contract_check.py"
python3 -B "$EVAL_DIR/evaluate_outcomes.py" --validate-fixtures
python3 -B "$EVAL_DIR/test_evaluation.py"
