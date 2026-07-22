#!/usr/bin/env python3
"""Static checks for lead-nurture rules that must not drift."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Deliver the promised asset or answer immediately",
    "stop when the person converts, replies, opts out, or becomes ineligible.",
    "Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims.",
    "Never infer consent merely because an address exists; verify the permitted purpose, channel, source, jurisdiction, and suppression status.",
    "Never optimize for opens alone; use clicks, conversions, revenue, retention, qualified replies, or pipeline as the primary outcome.",
    "Never send until authentication, suppression, tracking, rendering, links, personalization fallbacks, and accessibility checks pass.",
    "Return `HOLD` when a required fact or QA check is missing, and `BLOCK` when permission or suppression prohibits the nurture.",
)


def main() -> int:
    skill = SKILL.read_text()
    failures = [rule for rule in RULES if rule not in skill]
    if failures:
        raise SystemExit("FAIL: static contract missing: " + ", ".join(failures))
    print(f"PASS: static contract ({len(RULES)} lead-nurture rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
