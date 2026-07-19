#!/usr/bin/env python3
"""Offline contract and held-out manifest checks for remediation planning."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
RULES = (
    "Use only after verified audit findings identify remediation gaps.",
    "Classify every remediation item as agent, storefront, or shared delivery.",
    "Name an accountable owner, source of truth, observable acceptance test, baseline check, and post-change check for every remediation item.",
    "Do not use a remediation plan as authority to execute customer, order, payment, credential, or production changes.",
)
FIELDS = {"id", "split", "fixture_type", "prompt", "expected_skill_usage"}


def validate_contract() -> list[str]:
    failures = []
    try:
        skill = SKILL.read_text()
        cases = json.loads(CASES.read_text())["cases"]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        return [f"failed to load deterministic inputs: {error}"]

    for rule in RULES:
        if rule not in skill:
            failures.append(f"missing remediation guardrail: {rule}")

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
        if case["fixture_type"] not in {"synthetic", "sanitized_trace"}:
            failures.append(f"{case['id']} has invalid fixture type")
        if case["expected_skill_usage"] not in counts:
            failures.append(f"{case['id']} has invalid skill usage")
        else:
            counts[case["expected_skill_usage"]] += 1
        if case["expected_skill_usage"] == "use":
            findings = case.get("audit_fixture", {}).get("findings")
            if not isinstance(findings, list) or not findings:
                failures.append(f"{case['id']} lacks audit findings")
            elif not all(isinstance(finding, dict) and {"id", "bucket", "evidence_source"} <= finding.keys() for finding in findings):
                failures.append(f"{case['id']} has invalid audit findings")
        elif not isinstance(case.get("expected_route"), str) or not case["expected_route"]:
            failures.append(f"{case['id']} lacks an authorized route")
    if len(cases) < 10 or any(count < 5 for count in counts.values()):
        failures.append("held-out manifest needs at least five use and five do-not-use cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic custom-agent remediation contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic custom-agent remediation contract checks")
    print("Harness gate: run the isolated enabled/disabled evaluator documented in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
