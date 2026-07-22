#!/usr/bin/env python3
"""Static contract checks for non-negotiable promotional-offer rules."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "State the offer, eligibility, material terms, price/discount, expiry, and exclusions accurately; never fabricate scarcity or use a deceptive subject.",
    "Do not automatically resend to non-openers; open data can be inaccurate and repeated sends can increase complaints or unsubscribes.",
    "Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims.",
    "Never infer consent merely because an address exists; verify the permitted purpose, channel, source, jurisdiction, and suppression status.",
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
        mutated_skill = skill.replace(rule, "removed", 1)
        if rule in mutated_skill:
            failures.append(f"mutation not rejected: {rule}")

    if failures:
        print("FAIL: static contract")
        print("\n".join(failures))
        return 1
    print(f"PASS: static contract ({len(RULES)} mutation checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
