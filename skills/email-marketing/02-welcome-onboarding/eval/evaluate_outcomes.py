#!/usr/bin/env python3
"""Score frozen welcome-onboarding outcomes without implementing skill policy."""
import json
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"
OUTCOME_KEYS = frozenset(("decision", "reason_code", "required_elements"))


def score(actual: dict, expected: dict) -> bool:
    return actual == expected and set(actual) == OUTCOME_KEYS


def main() -> int:
    fixtures = json.loads(FIXTURES.read_text())
    if fixtures.get("schema_version") != 1:
        raise SystemExit("unsupported scenario schema")
    cases = fixtures.get("cases", [])
    failures = []
    for case in cases:
        if case.get("split") != "held-out":
            failures.append(f"{case.get('name', 'unnamed')}: not held-out")
            continue
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            failures.append(f"{case['name']}: missing prompt")
            continue
        expected = case.get("expected_outcome")
        actual = case.get("candidate_outcome")
        if not isinstance(expected, dict) or set(expected) != OUTCOME_KEYS:
            failures.append(f"{case['name']}: invalid evaluator keys")
        elif not isinstance(actual, dict) or not score(actual, expected):
            failures.append(f"{case['name']}: candidate outcome does not satisfy outcome contract")

    if len(cases) < 10:
        failures.append("fewer than 10 held-out cases")
    if failures:
        print("FAIL: outcome eval")
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(cases)} held-out outcome scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
