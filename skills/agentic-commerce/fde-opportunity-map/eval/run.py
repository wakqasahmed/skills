#!/usr/bin/env python3
"""Offline contract checks for the FDE opportunity-map outcome eval."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
RULES = (
    "only when a verified custom integration or workflow constraint exceeds configuration",
    "Do not present a discovery finding as an approved integration",
    "smallest reversible sprint",
    "approval gates, success evidence, and a rollback path",
)
FIELDS = {"id", "split", "prompt", "expected_skill_usage", "expected_outcome", "expected_safety_outcome", "outcome_evidence", "safety_evidence"}


def validate_contract() -> list[str]:
    failures = []
    try:
        skill = SKILL.read_text()
    except OSError as error:
        return [f"failed to read SKILL.md: {error}"]
    for rule in RULES:
        if rule not in skill:
            failures.append(f"missing FDE guardrail: {rule}")

    try:
        cases = json.loads(CASES.read_text()).get("cases", [])
    except (OSError, json.JSONDecodeError) as error:
        return [f"failed to read held-out cases: {error}"]
    counts = {"use": 0, "do_not_use": 0}
    identifiers = set()
    for case in cases:
        missing = FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} missing {sorted(missing)}")
            continue
        if case["id"] in identifiers:
            failures.append(f"duplicate case id: {case['id']}")
        identifiers.add(case["id"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if case["expected_skill_usage"] not in counts:
            failures.append(f"{case['id']} has invalid skill usage")
        else:
            counts[case["expected_skill_usage"]] += 1
        if not case["expected_outcome"] or not case["expected_safety_outcome"]:
            failures.append(f"{case['id']} lacks a machine-checkable outcome")
        if not all(isinstance(case[key], list) and case[key] for key in ("outcome_evidence", "safety_evidence")):
            failures.append(f"{case['id']} lacks grader evidence")
    if len(cases) < 10 or any(count < 5 for count in counts.values()):
        failures.append("held-out manifest needs at least five use and five do-not-use cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic FDE contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic FDE contract checks")
    print("Harness gate: run the isolated enabled/disabled evaluator documented in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
