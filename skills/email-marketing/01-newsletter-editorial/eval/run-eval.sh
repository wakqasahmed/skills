#!/usr/bin/env bash
set -euo pipefail

EVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$EVAL_DIR/contract_check.py"
python3 "$EVAL_DIR/evaluate_outcomes.py"
python3 "$EVAL_DIR/test_harness_contract.py"
