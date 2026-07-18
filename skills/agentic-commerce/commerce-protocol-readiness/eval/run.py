#!/usr/bin/env python3
"""Offline contract checks for the commerce-protocol-readiness behavior eval.

This is deliberately not an agent evaluator. It verifies the checked-in
SKILL.md contract and held-out case manifest only; model outcomes are produced
and scored by the explicitly gated harness documented in eval/README.md.
"""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL_MD = EVAL_DIR.parent / "SKILL.md"
CASES_PATH = EVAL_DIR / "held-out-cases.json"
SHARED_GUARDRAILS = EVAL_DIR.parent.parent / "references" / "guardrails.md"
REQUIRED_SKILL_TERMS = (
    "Classify the commerce goal",
    "Score each protocol as",
    "Recommend the smallest next implementation",
    "../references/guardrails.md",
)
REQUIRED_CASE_FIELDS = {
    "id",
    "split",
    "prompt",
    "expected_skill_usage",
    "expected_outcome",
    "expected_safety_outcome",
}
REQUIRED_SAFETY_TERMS = (
    "identity verification",
    "consent capture",
    "audit logging",
    "fraud controls",
    "human escalation path",
)


def validate_contract() -> list[str]:
    failures = []
    skill_text = SKILL_MD.read_text()
    for term in REQUIRED_SKILL_TERMS:
        if term not in skill_text:
            failures.append(f"SKILL.md is missing required contract text: {term}")

    guardrails_text = SHARED_GUARDRAILS.read_text().lower()
    for term in REQUIRED_SAFETY_TERMS:
        if term not in guardrails_text:
            failures.append(f"shared guardrails are missing required safety text: {term}")

    cases = json.loads(CASES_PATH.read_text()).get("cases", [])
    if len(cases) < 10:
        failures.append("held-out manifest must contain at least 10 cases")

    identifiers = set()
    usage_counts = {"use": 0, "do_not_use": 0}
    for case in cases:
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} is missing {sorted(missing)}")
            continue
        if case["id"] in identifiers:
            failures.append(f"duplicate case id: {case['id']}")
        identifiers.add(case["id"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if case["expected_skill_usage"] not in usage_counts:
            failures.append(f"{case['id']} has invalid skill-usage expectation")
        else:
            usage_counts[case["expected_skill_usage"]] += 1
        if not case["expected_safety_outcome"].strip():
            failures.append(f"{case['id']} has no explicit safety outcome")

    for usage, count in usage_counts.items():
        if count < 5:
            failures.append(f"held-out manifest needs at least 5 {usage} cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic contract checks")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: deterministic contract checks")
    print("Harness gate: run the credentialed, isolated ablation described in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
