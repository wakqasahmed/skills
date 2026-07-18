#!/usr/bin/env python3
"""No-network behavioral eval for the email-marketing safety decisions."""
import json
import sys
from pathlib import Path


def campaign_decision(facts: dict) -> str:
    if facts["suppressed"]:
        return "BLOCK"
    if not facts["permission"] or not facts["legal_basis_verified"]:
        return "BLOCK"
    if facts["jurisdiction"] == "unknown":
        return "HOLD" if facts.get("jurisdiction_fact_collectable") else "BLOCK"
    if not all(facts[key] for key in ("authentication", "identity", "factual_claims_verified")):
        return "BLOCK"
    return "SEND" if facts["qa_complete"] else "HOLD"


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


def validate_cases(cases: list[dict], evaluate, fields: tuple[str, ...]) -> bool:
    passed = True
    for case in cases:
        expected = evaluate(case["input"])
        actual = tuple(case["candidate"][field] for field in fields)
        valid = actual == ((expected,) if isinstance(expected, str) else expected)
        if valid != case["expected_valid"]:
            print(f"FAIL {case['name']}: expected valid={case['expected_valid']}, got {valid}")
            passed = False
        else:
            print(f"PASS {case['name']}")
    return passed


def main() -> int:
    fixture_path = Path(__file__).parent / "fixtures" / "scenarios.json"
    fixtures = json.loads(fixture_path.read_text())
    if fixtures["schema_version"] != 1:
        raise SystemExit("unsupported scenario schema")
    campaigns_ok = validate_cases(fixtures["campaigns"], campaign_decision, ("decision",))
    orchestration_ok = validate_cases(
        fixtures["orchestration"], orchestration_decision, ("marketing", "service")
    )
    return 0 if campaigns_ok and orchestration_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
