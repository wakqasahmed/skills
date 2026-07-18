#!/usr/bin/env python3
"""Validate frozen, synthetic agent outcomes without reimplementing policy."""
import json
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"


def main() -> int:
    cases = json.loads(FIXTURES.read_text())["cases"]
    failures = []
    for case in cases:
        expected = case["expected"]
        if not {"decision", "reason_code", "required_actions"}.issubset(expected):
            failures.append(case["name"])

    if failures:
        print("FAIL: outcome scenarios: " + ", ".join(failures))
        return 1
    print(f"PASS: {len(cases)} held-out outcome scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
