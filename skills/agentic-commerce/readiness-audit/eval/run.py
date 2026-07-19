#!/usr/bin/env python3
"""Offline deterministic contract checks for the readiness-audit skill."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
RULES = (
    "Confirm the submitted URL is a public production storefront.",
    "Score each dimension below from public signals only, citing at least one URL or check per score.",
    "Do not imply access to Search Console, analytics, revenue, logs, rankings, or conversions unless the user provided verified exports.",
    "Prefer practical remediation over generic score commentary.",
)
FIELDS = {"id", "split", "prompt", "fixture", "fixture_evidence", "expected_skill_usage", "expected_outcome", "expected_safety_outcome", "outcome_evidence", "safety_evidence"}


def missing_rules(skill: str) -> list[str]:
    return [rule for rule in RULES if rule not in skill]


def validate_contract() -> list[str]:
    failures = []
    skill = SKILL.read_text()
    for rule in RULES:
        if rule in missing_rules(skill):
            failures.append(f"missing contract rule: {rule}")
        elif rule not in missing_rules(skill.replace(rule, "removed", 1)):
            failures.append(f"mutation not rejected: {rule}")

    data = json.loads(CASES.read_text())
    cases = data.get("cases", []) if isinstance(data, dict) else []
    usage = {"use": 0, "do_not_use": 0}
    for case in cases:
        if not isinstance(case, dict):
            failures.append("case must be an object")
            continue
        missing = FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} missing {sorted(missing)}")
            continue
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if case["expected_skill_usage"] not in usage:
            failures.append(f"{case['id']} has invalid skill usage")
        else:
            usage[case["expected_skill_usage"]] += 1
        fixture = EVAL_DIR / case["fixture"]
        if not fixture.is_file():
            failures.append(f"{case['id']} fixture is missing")
        elif not all(evidence in fixture.read_text() for evidence in case["fixture_evidence"]):
            failures.append(f"{case['id']} fixture evidence is not frozen in its fixture")
        if not all(isinstance(case[field], list) and case[field] for field in ("outcome_evidence", "safety_evidence")):
            failures.append(f"{case['id']} lacks fixture-grounded evidence")
    if len(cases) < 10 or usage["use"] < 5 or usage["do_not_use"] < 5:
        failures.append("held-out manifest needs at least ten cases with five use and five do-not-use cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic readiness-audit contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic readiness-audit contract checks")
    print("Harness gate: run the isolated enabled/disabled evaluator documented in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
