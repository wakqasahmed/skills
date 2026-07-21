#!/usr/bin/env python3
"""Validate frozen newsletter outcomes without reimplementing the skill policy."""
import json
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"
OUTCOME_FIELDS = ("decision", "reason_code", "required_actions")


def outcome_matches(candidate: dict, expected: dict) -> bool:
    return all(candidate.get(field) == expected[field] for field in OUTCOME_FIELDS)


def main() -> int:
    cases = json.loads(FIXTURES.read_text())["cases"]
    failures = []
    for case in cases:
        if case.get("split") != "held-out":
            failures.append(f"{case['name']}: not held-out")
            continue
        expected = case["expected"]
        if set(expected) != set(OUTCOME_FIELDS):
            failures.append(f"{case['name']}: invalid expected outcome")
            continue
        valid = outcome_matches(case["candidate_outcome"], expected)
        if valid != case["expected_valid"]:
            failures.append(f"{case['name']}: expected valid={case['expected_valid']}, got {valid}")

    if failures:
        print("FAIL: outcome scenarios")
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(cases)} held-out outcome scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
