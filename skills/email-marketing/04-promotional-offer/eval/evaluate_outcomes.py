#!/usr/bin/env python3
"""Validate agent outcomes without reimplementing the skill policy."""
import json
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"
OUTCOMES = Path(__file__).parent / "fixtures" / "frozen-agent-outcomes.json"
REQUIRED_FIELDS = {"decision", "reason_code", "required_actions"}


def score(records: list[dict], cases: list[dict]) -> tuple[int, list[str]]:
    expected = {case["name"]: case["expected"] for case in cases}
    passes = 0
    failures = []
    for record in records:
        name = record.get("name")
        outcome = record.get("outcome")
        if name not in expected:
            failures.append(f"{name}: unknown case")
        elif not isinstance(outcome, dict) or not REQUIRED_FIELDS.issubset(outcome):
            failures.append(f"{name}: missing outcome fields")
        elif outcome != expected[name]:
            failures.append(f"{name}: outcome did not match expected result")
        else:
            passes += 1
    return passes, failures


def validate(records: list[dict], cases: list[dict]) -> list[str]:
    expected_names = {case["name"] for case in cases}
    record_names = [record.get("name") for record in records]
    failures = []
    if set(record_names) != expected_names or len(record_names) != len(expected_names):
        failures.append("outcomes do not cover every held-out case exactly once")
    _, score_failures = score(records, cases)
    return failures + score_failures


def main() -> int:
    cases = json.loads(FIXTURES.read_text())["cases"]
    records = json.loads(OUTCOMES.read_text())["outcomes"]
    failures = validate(records, cases)

    if failures:
        print("FAIL: held-out outcomes")
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(records)} held-out agent outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
