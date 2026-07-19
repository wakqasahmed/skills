#!/usr/bin/env python3
"""Offline contract checks for the product-knowledge outcome eval."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
RULES = (
    "Treat facts without a visible source as unknown; never infer ingredients, compatibility, contraindications, or safety claims.",
    "Separate template-level fixes from product-specific enrichment.",
    "Do not alter catalog data or make product claims; identify the source of truth and route remediation to its owner.",
)
FIELDS = {"id", "split", "prompt", "expected_skill_usage", "catalog", "feed", "expected_artifact"}


def missing_rules(skill: str) -> list[str]:
    return [rule for rule in RULES if rule not in skill]


def validate_contract() -> list[str]:
    failures = []
    skill = SKILL.read_text()
    for rule in RULES:
        if rule in missing_rules(skill):
            failures.append(f"missing product-knowledge guardrail: {rule}")
        elif rule not in missing_rules(skill.replace(rule, "removed", 1)):
            failures.append(f"mutation not rejected: {rule}")
    cases = json.loads(CASES.read_text()).get("cases", [])
    counts, identifiers = {"use": 0, "do_not_use": 0}, set()
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
        if case["expected_skill_usage"] in counts:
            counts[case["expected_skill_usage"]] += 1
        else:
            failures.append(f"{case['id']} has invalid skill usage")
        artifact = case["expected_artifact"]
        if not isinstance(case["catalog"], list) or not isinstance(case["feed"], dict):
            failures.append(f"{case['id']} lacks realistic catalog/feed input")
        if not isinstance(artifact, dict) or not isinstance(artifact.get("decision"), str):
            failures.append(f"{case['id']} lacks a machine-checkable artifact")
        elif artifact["decision"] == "analyze":
            gaps = artifact.get("observed_gaps")
            if (not isinstance(gaps, list) or not gaps
                    or any(not isinstance(gap, dict) or set(gap) != {"sku", "field", "source", "remediation"} for gap in gaps)):
                failures.append(f"{case['id']} lacks observed product gap artifacts")
        elif artifact["decision"] == "route":
            if artifact.get("observed_gaps") != [] or not artifact.get("route") or not artifact.get("non_use_reason"):
                failures.append(f"{case['id']} lacks non-use routing artifact")
        else:
            failures.append(f"{case['id']} has invalid artifact decision")
    if len(cases) < 10 or any(count < 5 for count in counts.values()):
        failures.append("held-out manifest needs at least five use and five do-not-use cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic product-knowledge contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic product-knowledge contract checks")
    print("Harness gate: run the isolated enabled/disabled evaluator documented in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
