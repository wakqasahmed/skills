#!/usr/bin/env python3
"""Static checks for the welcome-onboarding skill's non-negotiable rules."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Trigger only from a verified signup, account creation, or other documented permission event",
    "Deliver any promised incentive or resource in the first message",
    "Exit or change the path when the recipient completes the target action, unsubscribes, complains, or becomes ineligible.",
    "Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims.",
    "Never infer consent merely because an address exists",
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
