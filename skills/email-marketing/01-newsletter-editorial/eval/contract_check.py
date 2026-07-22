#!/usr/bin/env python3
"""Static contract checks for non-negotiable newsletter rules."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Use this skill only after applying the `00-email-marketing-guardrails` skill",
    "Use it when the audience has explicitly subscribed to ongoing content and the brand can sustain the promised topic and cadence.",
    "Send through the marketing stream, not the transactional stream",
    "Define one issue-level objective, one primary CTA, and a small number of supporting links; do not turn every issue into an undifferentiated link dump.",
    "Don't change topic or frequency beyond what the subscriber agreed to.",
    "Don't judge issue performance on opens alone.",
    "Never claim a universal best send time; use recipient-level optimization or a controlled timing test.",
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
