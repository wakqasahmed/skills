#!/usr/bin/env python3
"""No-network behavioral eval for the email-marketing safety decisions."""
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent
SKILLS_DIR = EVAL_DIR.parent

SKILL_CONTRACTS = {
    "00-email-marketing-guardrails/SKILL.md": (
        "Return `BLOCK` with the failed hard-gate reason",
        "Return `HOLD` with the missing fact or check",
        "Return `SEND` only when every applicable gate passes and the campaign has a measurable hypothesis",
    ),
    "18-jurisdiction-compliance-routing/SKILL.md": (
        "Return `HOLD` only while the team can collect the missing routing fact",
        "return `BLOCK` when jurisdiction, legal basis, or applicable exception cannot be verified",
        "Final `SEND`, `HOLD`, or `BLOCK` decision, with the unresolved fact, failed gate, or counsel question",
    ),
    "19-lifecycle-orchestration/SKILL.md": (
        "treat mixed messages as marketing and never relabel a promotion to win priority",
        "return `HOLD: PRECEDENCE_POLICY_MISSING` when no applicable table exists",
        "decision (`SEND`, `DEFER`, `DROP`, or `BLOCK`), reason code",
    ),
}


def campaign_decision(facts: dict) -> tuple[str, str]:
    if facts["suppressed"]:
        return ("BLOCK", "SUPPRESSED")
    if not facts["permission"] or not facts["legal_basis_verified"]:
        return ("BLOCK", "PERMISSION_OR_LEGAL_BASIS_UNVERIFIED")
    if facts["jurisdiction"] == "unknown":
        return (
            ("HOLD", "JURISDICTION_FACT_MISSING")
            if facts.get("jurisdiction_fact_collectable")
            else ("BLOCK", "JURISDICTION_UNVERIFIABLE")
        )
    if not all(facts[key] for key in ("authentication", "identity", "factual_claims_verified")):
        return ("BLOCK", "AUTHENTICATION_IDENTITY_OR_CLAIMS_UNVERIFIED")
    if not facts["qa_complete"]:
        return ("HOLD", "QA_INCOMPLETE")
    if not facts.get("measurable_hypothesis"):
        return ("HOLD", "MEASURABLE_HYPOTHESIS_MISSING")
    return ("SEND", "ALL_APPLICABLE_GATES_PASSED")


def orchestration_decision(facts: dict) -> tuple[str, str]:
    if facts["promotional_content"]:
        return ("BLOCK: MARKETING_CLASSIFICATION", "NOT_APPLICABLE")
    marketing = "SEND"
    if facts["marketing_suppressed"]:
        marketing = "BLOCK: UNSUBSCRIBED"
    elif not facts["precedence_policy"]:
        marketing = "HOLD: PRECEDENCE_POLICY_MISSING"
    elif not facts["cap_available"]:
        marketing = "DEFER: CAP_REACHED"
    service = "SEND" if facts["service_verified"] else "NOT_APPLICABLE"
    return marketing, service


def missing_contract_rules(skill_md: str, rules: tuple[str, ...]) -> list[str]:
    return [rule for rule in rules if rule not in skill_md]


def validate_skill_contracts() -> bool:
    passed = True
    for relative_path, rules in SKILL_CONTRACTS.items():
        skill_md = (SKILLS_DIR / relative_path).read_text()
        missing_rules = missing_contract_rules(skill_md, rules)
        if missing_rules:
            for rule in missing_rules:
                print(f"FAIL {relative_path}: missing safety rule: {rule}")
            passed = False
            continue

        print(f"PASS {relative_path}: all {len(rules)} safety rules present")
        for rule in rules:
            mutated_skill_md = skill_md.replace(rule, "rule removed by mutation", 1)
            if rule not in missing_contract_rules(mutated_skill_md, rules):
                print(f"FAIL {relative_path}: mutation was not caught: {rule}")
                passed = False
            else:
                print(f"PASS {relative_path}: mutation rejected: {rule}")
    return passed


def validate_cases(cases: list[dict], evaluate, fields: tuple[str, ...]) -> bool:
    passed = True
    for case in cases:
        expected = evaluate(case["input"])
        actual = tuple(case["candidate"][field] for field in fields)
        valid = actual == expected
        if valid != case["expected_valid"]:
            print(f"FAIL {case['name']}: expected valid={case['expected_valid']}, got {valid}")
            passed = False
        else:
            print(f"PASS {case['name']}")
    return passed


def main() -> int:
    fixture_path = EVAL_DIR / "fixtures" / "scenarios.json"
    fixtures = json.loads(fixture_path.read_text())
    if fixtures["schema_version"] != 1:
        raise SystemExit("unsupported scenario schema")
    contracts_ok = validate_skill_contracts()
    campaigns_ok = validate_cases(fixtures["campaigns"], campaign_decision, ("decision", "reason_code"))
    orchestration_ok = validate_cases(
        fixtures["orchestration"], orchestration_decision, ("marketing", "service")
    )
    return 0 if contracts_ok and campaigns_ok and orchestration_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
