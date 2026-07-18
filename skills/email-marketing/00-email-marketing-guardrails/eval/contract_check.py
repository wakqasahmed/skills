#!/usr/bin/env python3
"""Static contract checks for non-negotiable email safety rules."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Never use bought, scraped, harvested, or unverifiable lists.",
    "Maintain suppression for unsubscribes, complaints, hard bounces, and jurisdiction-specific do-not-contact requests.",
    "Authenticate all sending domains; use SPF or DKIM for all senders and SPF, DKIM, and DMARC alignment for bulk sending",
    "Return `BLOCK` with the failed hard-gate reason",
    "Return `HOLD` with the missing fact or check",
    "Return `SEND` only when every applicable gate passes and the campaign has a measurable hypothesis",
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
