#!/usr/bin/env python3
"""Static contract checks for product launch requirements."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims.",
    "Don't send a final reminder unless a real deadline or availability constraint exists.",
    "Don't announce to users for whom the product is unavailable or irrelevant.",
    "Don't test several launch variables at once.",
    "Never optimize for opens alone; use clicks, conversions, revenue, retention, qualified replies, or pipeline as the primary outcome.",
    "Never send until authentication, suppression, tracking, rendering, links, personalization fallbacks, and accessibility checks pass.",
)


def main() -> int:
    skill = SKILL.read_text()
    failures = []
    for rule in RULES:
        if rule not in skill:
            failures.append(f"missing rule: {rule}")
            continue
        if rule in skill.replace(rule, "removed", 1):
            failures.append(f"mutation not rejected: {rule}")

    if failures:
        print("FAIL: static contract")
        print("\n".join(failures))
        return 1
    print(f"PASS: static contract ({len(RULES)} mutation checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
